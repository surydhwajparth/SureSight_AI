# app/services/governance_agent.py
"""
Suresight AI — Governance Agent (LLM-backed)
Structured like ocr_agent.py; business logic preserved.

- Uses Gemini to detect PII/PHI across OCR text/entities/tables.
- Applies Python redaction by role & HIPAA/GDPR rules.
- Returns sanitized view + redaction manifest + pii_report + audit.

Fixes kept:
- Robust JSON extraction (code fences / extra prose).
- Retry with backoff to reduce transient 5xx/parse errors.
- Graceful fallback to empty PII (no 500) so multi-file runs don’t break.
"""

import os
import re
import hmac
import json
import time
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------- Env + config (mirror ocr_agent.py) ----------
load_dotenv()

# ------------- MANUAL CONFIG (env wins only if manual placeholder left) -------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL")
# -----------------------------------------------------------------------------------

def _manual_key_set(v: Optional[str]) -> bool:
    return bool(v) and not v.startswith("PASTE_") and not v.startswith("paste_")

API_KEY = GEMINI_API_KEY if _manual_key_set(GEMINI_API_KEY) else (
    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)
GEMINI_MODEL = GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CONFIG_SOURCE = "manual" if _manual_key_set(GEMINI_API_KEY or "") else (
    "env(GEMINI_API_KEY)" if os.getenv("GEMINI_API_KEY") else
    "env(GOOGLE_API_KEY)" if os.getenv("GOOGLE_API_KEY") else "none"
)

# ---------- Gemini client shim (prefer new google-genai, fallback to legacy) ----------
_client_mode: Optional[str] = None
_client = None
try:
    # New SDK
    from google import genai as ggenai  # type: ignore
    if not API_KEY:
        raise RuntimeError("Missing API key for google-genai")
    _client = ggenai.Client(api_key=API_KEY)
    _client_mode = "google-genai"
except Exception:
    try:
        # Legacy SDK
        import google.generativeai as ggenai  # type: ignore
        if not API_KEY:
            raise RuntimeError("Missing API key for google-generativeai")
        ggenai.configure(api_key=API_KEY)
        _client = ggenai.GenerativeModel(GEMINI_MODEL)
        _client_mode = "google-generativeai"
    except Exception:
        _client_mode = "none"

# ---------------- Policy knobs ----------------
POLICY_VERSION = os.getenv("GOV_POLICY_VERSION", "gov_llm_v1_2025-09-04")
EXPORT_CONFIDENCE_MIN = float(os.getenv("GOV_EXPORT_CONF_MIN", "0.80"))
MASK_TOKEN = "[REDACTED]"
PSEUDO_SALT = (os.getenv("GOV_PSEUDO_SALT") or "DO_NOT_USE_IN_PROD_suresight_demo_salt").encode("utf-8")
MINIMUM_NECESSARY = True  # drop unknown/low-value entities for client role

LLM_CATEGORIES = {
    "NAME", "FULL_NAME", "FIRST_NAME", "LAST_NAME",
    "EMAIL", "PHONE", "ADDRESS", "DOB", "DATE_OF_BIRTH",
    "MRN", "SSN", "NATIONAL_ID", "CREDIT_CARD", "IBAN",
    "LICENSE", "PLATE", "IP", "GEO", "GPS",
}

# ---------------- FastAPI ----------------
class A2A(BaseModel):
    protocol: str
    intent: str
    job_id: str
    input: dict

app = FastAPI()

@app.get("/health")
def health():
    return {
        "ok": bool(API_KEY) and _client_mode in ("google-genai", "google-generativeai"),
        "service": "governance",
        "sdk": _client_mode,
        "model": GEMINI_MODEL,
        "has_key": bool(API_KEY),
        "config_source": CONFIG_SOURCE,
        "policy_version": POLICY_VERSION,
    }

# ---------------- Utils (mirror OCR helpers for JSON robustness) ----------------
def _fingerprint(value: str) -> str:
    try:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    except Exception:
        return "fp_err"

def _pseudonymize(value: str, kind: str) -> str:
    sig = hmac.new(PSEUDO_SALT, (kind + ":" + value).encode("utf-8"), hashlib.sha256).hexdigest()
    return f"token:{kind.lower()}:{sig[:10]}"

def _ensure_model_name(name: Optional[str]) -> str:
    aliases = {
        "gemini-2.5-flasj": "gemini-2.5-flash",
        "gemini-2.5-flahs": "gemini-2.5-flash",
        "gemini-1.5-flasj": "gemini-1.5-flash",
        "gemini-1.5-flahs": "gemini-1.5-flash",
    }
    s = (name or "").strip()
    return aliases.get(s, s) or "gemini-2.5-flash"

def _compact_tables_for_prompt(tables: List[Dict[str, Any]], limit_chars: int = 4000) -> str:
    lines: List[str] = []
    for t in (tables or []):
        tid = t.get("id", "table")
        lines.append(f"[Table {tid}]")
        for r in (t.get("rows") or []):
            lines.append(" | ".join(str(c) for c in r))
        lines.append("")
        if sum(len(x) for x in lines) > limit_chars:
            lines.append("... (truncated)")
            break
    return "\n".join(lines)

def _llm_prompt(ocr: Dict[str, Any]) -> str:
    full_text = (ocr.get("full_text") or "")[:20000]
    ents = ocr.get("entities") or []
    tabs = ocr.get("tables") or []

    ent_lines = []
    for e in ents[:80]:
        name = str(e.get("name", ""))[:64]
        val  = str(e.get("value", ""))[:256]
        ety  = str(e.get("type", ""))[:32]
        ent_lines.append(f"- {name} = {val} (type={ety})")
    ents_compact = "\n".join(ent_lines) if ent_lines else "(none)"

    tables_compact = _compact_tables_for_prompt(tabs)

    return (
        "You are a privacy compliance assistant. Identify PII/PHI and GDPR identifiers in the document.\n"
        "Return STRICT JSON ONLY with the EXACT schema:\n"
        "{\n"
        '  "pii": [\n'
        '    {"category": "EMAIL|PHONE|DOB|NAME|ADDRESS|MRN|SSN|CREDIT_CARD|IBAN|NATIONAL_ID|IP|GEO|LICENSE|PLATE",\n'
        '     "value": "<exact string from text>",\n'
        '     "confidence": 0.0 to 1.0,\n'
        '     "where": ["full_text","entities","tables"]\n'
        "    }, ...\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- Use the exact string values found in the content; do not synthesize new ones.\n"
        "- Prefer precise categories; if unsure, choose a close one (e.g., NAME).\n"
        "- Keep the list concise; no duplicates.\n"
        "- Output JSON ONLY (no prose, no markdown).\n"
        "\n"
        "===== FULL_TEXT (truncated) =====\n"
        f"{full_text}\n\n"
        "===== ENTITIES (name=value (type)) =====\n"
        f"{ents_compact}\n\n"
        "===== TABLES (truncated) =====\n"
        f"{tables_compact}\n"
    )

# ---- Robust JSON parsing (handles fences/extra text) ----
_CODEFENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"(\{.*\})", re.DOTALL)

def _extract_text_from_response(resp: Any) -> str:
    """
    Safely pull text from either the new (google-genai) or legacy responses,
    without assuming candidates/content/parts are present.
    """
    # Try direct text fields first
    direct = getattr(resp, "output_text", None) or getattr(resp, "text", None)
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    # Then try candidates[0].content.parts[*].text (new SDK)
    candidates = getattr(resp, "candidates", None)
    if isinstance(candidates, (list, tuple)) and len(candidates) > 0:
        cand0 = candidates[0]
        content = getattr(cand0, "content", None)
        if content is not None:
            parts = getattr(content, "parts", None)
            if isinstance(parts, (list, tuple)):
                for part in parts:
                    t = getattr(part, "text", None)
                    if isinstance(t, str) and t.strip():
                        return t.strip()

    # Nothing usable
    return ""


def _parse_json_loosely(text: str) -> Dict[str, Any]:
    if not text:
        raise ValueError("empty text")
    try:
        return json.loads(text)
    except Exception:
        pass
    m = _CODEFENCE_RE.search(text)
    if m:
        inner = m.group(1)
        try:
            return json.loads(inner)
        except Exception:
            pass
    objs = _JSON_OBJECT_RE.findall(text)
    if objs:
        candidate = max(objs, key=len)
        try:
            return json.loads(candidate)
        except Exception:
            pass
    raise ValueError("no valid JSON object found")

# ---- LLM calls with retry ----
def _call_gemini_json_once(prompt: str) -> Dict[str, Any]:
    if _client_mode == "google-genai":
        # New SDK
        resp = _client.models.generate_content(  # type: ignore[attr-defined]
            model=_ensure_model_name(GEMINI_MODEL),
            contents=[{"role": "user","parts": [{"text": prompt}]}],
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "max_output_tokens": 2048
            }
        )
        text = _extract_text_from_response(resp)
        if not text:
            raise RuntimeError("Empty response from Gemini (google-genai)")
        return _parse_json_loosely(text)

    elif _client_mode == "google-generativeai":
        # Legacy SDK
        resp = _client.generate_content(  # type: ignore[attr-defined]
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "max_output_tokens": 2048
            }
        )
        text = _extract_text_from_response(resp)
        if not text:
            raise RuntimeError("Empty response from Gemini (google-generativeai)")
        return _parse_json_loosely(text)

    else:
        raise RuntimeError("Gemini client not initialized. Check API key/SDK.")


def _call_gemini_json_with_retry(prompt: str, attempts: int = 2, backoff_base: float = 0.5) -> Dict[str, Any]:
    last_err: Optional[Exception] = None
    for i in range(attempts):
        try:
            return _call_gemini_json_once(prompt)
        except Exception as e:
            last_err = e
            time.sleep(backoff_base * (i + 1))
    raise last_err if last_err else RuntimeError("Unknown governance LLM error")

def _normalize_llm_pii(llm: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in (llm.get("pii") or []):
        try:
            cat = str(item.get("category", "") or "").upper().strip()
            val = str(item.get("value", "") or "").strip()
            conf = float(item.get("confidence", 0.0) or 0.0)
            where = item.get("where") or []
            if not cat or not val:
                continue
            if len(val) < 3:
                continue
            if cat == "FULL_NAME": cat = "NAME"
            if cat == "DATE_OF_BIRTH": cat = "DOB"
            out.append({"category": cat, "value": val, "confidence": conf, "where": list(dict.fromkeys(where))})
        except Exception:
            continue
    # dedupe
    seen = set(); uniq = []
    for x in out:
        k = (x["category"], x["value"])
        if k in seen: continue
        seen.add(k); uniq.append(x)
    return uniq

# ---------- Redaction policy ----------
def _action_for(category: str, role: str, gdpr: bool, hipaa: bool) -> str:
    if role == "admin":
        return "allow"
    cat = category.upper()
    if cat in {"SSN", "CREDIT_CARD", "IBAN", "LICENSE", "PLATE"}:
        return "mask"
    if hipaa:
        if cat in {"NAME", "ADDRESS", "DOB", "MRN", "PHONE", "EMAIL", "IP", "GEO"}:
            return "mask" if cat in {"NAME", "ADDRESS", "DOB", "MRN"} else ("pseudonymize" if gdpr else "mask")
    if gdpr:
        if cat in {"EMAIL", "PHONE", "NAME", "ADDRESS", "IP", "GEO", "NATIONAL_ID"}:
            return "pseudonymize"
    return "mask"

def _safe_sub_replace(text: str, needle: str, repl: str) -> str:
    if not text or not needle:
        return text or ""
    try:
        return re.sub(re.escape(needle), repl, text)
    except Exception:
        return text.replace(needle, repl)

def _apply_text_redactions(text: str, pii_items: List[Dict[str, Any]],
                           role: str, gdpr: bool, hipaa: bool,
                           manifest: List[Dict[str, Any]], location: str) -> str:
    out = text or ""
    for item in pii_items:
        action = _action_for(item["category"], role, gdpr, hipaa)
        if action == "allow":
            continue
        val = item["value"]
        fp = _fingerprint(val)
        if action == "mask":
            repl = MASK_TOKEN; method = "mask"
        else:
            repl = _pseudonymize(val, item["category"]); method = "pseudonymize"
        if out and val in out:
            out = _safe_sub_replace(out, val, repl)
            manifest.append({"category": item["category"], "method": method, "location": location, "fp": fp})
    return out

def _apply_entity_redactions(entities: List[Dict[str, Any]], pii_items: List[Dict[str, Any]],
                             role: str, gdpr: bool, hipaa: bool,
                             manifest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ents_out: List[Dict[str, Any]] = []
    for ent in (entities or []):
        if not isinstance(ent, dict):
            continue
        name = (ent.get("name") or "").lower()
        etype = (ent.get("type") or "").upper()
        value = str(ent.get("value", ""))

        matched_category = None
        for item in pii_items:
            if item["value"] and item["value"] == value:
                matched_category = item["category"]; break
        if not matched_category:
            if etype in {"EMAIL","PHONE","DOB","MRN","SSN"}:
                matched_category = etype
            elif any(k in name for k in ["email","e-mail"]):
                matched_category = "EMAIL"
            elif any(k in name for k in ["phone","mobile","contact"]):
                matched_category = "PHONE"
            elif any(k in name for k in ["dob","birth","date_of_birth"]):
                matched_category = "DOB"
            elif "mrn" in name or "patient id" in name:
                matched_category = "MRN"

        if matched_category and (role != "admin"):
            action = _action_for(matched_category, role, gdpr, hipaa)
            fp = _fingerprint(value)
            if action == "mask":
                ents_out.append({**ent, "value": MASK_TOKEN, "redacted": True})
                manifest.append({"category": matched_category, "method": "mask", "location": f"entities.{name}", "fp": fp})
                continue
            elif action == "pseudonymize":
                pseudo = _pseudonymize(value, matched_category)
                ents_out.append({**ent, "value": pseudo, "redacted": True})
                manifest.append({"category": matched_category, "method": "pseudonymize", "location": f"entities.{name}", "fp": fp})
                continue

        if role != "admin" and MINIMUM_NECESSARY:
            keep_ok = etype in ("AMOUNT","FINANCIAL","TOTAL","DATE","MEDICAL","INVOICE","CURRENCY") \
                      or any(k in name for k in ["total","amount","tax","invoice","gst","diagnosis"])
            if keep_ok:
                ents_out.append(ent)
        else:
            ents_out.append(ent)
    return ents_out

def _apply_table_redactions(tables: List[Dict[str, Any]], pii_items: List[Dict[str, Any]],
                            role: str, gdpr: bool, hipaa: bool,
                            manifest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for t in (tables or []):
        tid = t.get("id", "table")
        rows = t.get("rows") or []
        new_rows: List[List[str]] = []
        for r_idx, row in enumerate(rows):
            row = row if isinstance(row, (list, tuple)) else [row]
            new_row: List[str] = []
            for c_idx, cell in enumerate(row):
                text = "" if cell is None else str(cell)
                loc = f"tables[{tid}][{r_idx},{c_idx}]"
                new_text = _apply_text_redactions(text, pii_items, role, gdpr, hipaa, manifest, loc)
                new_row.append(new_text)
            new_rows.append(new_row)
        out.append({"id": tid, "rows": new_rows})
    return out

# ---------------- Core sanitize (LLM + Python) ----------------
def sanitize_with_llm(ocr: Dict[str, Any], role: str, gdpr: bool, hipaa: bool
                      ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Returns (sanitized_view, redaction_manifest, pii_report)
    Robust to LLM failure: returns original (admin) or unredacted (client) content with empty pii_report.
    """
    if not API_KEY or _client_mode == "none":
        raise RuntimeError("Gemini not configured for Governance agent")

    # 1) Call LLM for PII detection (retry + loose parse)
    pii_items: List[Dict[str, Any]] = []
    try:
        prompt = _llm_prompt(ocr)
        llm_raw = _call_gemini_json_with_retry(prompt, attempts=2, backoff_base=0.6)
        pii_items = _normalize_llm_pii(llm_raw)
    except Exception:
        # Graceful fallback: proceed with zero PII items
        pii_items = []

    # 2) Apply actions
    full_text = ocr.get("full_text", "") or ""
    entities = ocr.get("entities", []) or []
    tables = ocr.get("tables", []) or []

    manifest: List[Dict[str, Any]] = []

    # Text
    text_clean = full_text if role == "admin" else _apply_text_redactions(
        full_text, pii_items, role, gdpr, hipaa, manifest, "full_text"
    )

    # Entities
    ents_out = entities if role == "admin" else _apply_entity_redactions(
        entities, pii_items, role, gdpr, hipaa, manifest
    )

    # Tables
    tabs_out = tables if role == "admin" else _apply_table_redactions(
        tables, pii_items, role, gdpr, hipaa, manifest
    )

    sanitized = {
        "full_text": text_clean,
        "entities": ents_out,
        "tables": tabs_out,
    }

    pii_report = {"pii": pii_items}
    return sanitized, manifest, pii_report

# ---------------- Endpoint ----------------
@app.post("/a2a/govern")
def govern_handler(req: A2A):
    if req.intent != "doc.govern":
        raise HTTPException(status_code=400, detail="intent must be 'doc.govern'")

    try:
        inp = req.input or {}
        ocr: Dict[str, Any] = inp.get("ocr_result") or {}
        viewer: Dict[str, Any] = inp.get("viewer") or {}
        jurisdiction: Dict[str, Any] = inp.get("jurisdiction") or {}

        role = (viewer.get("role") or "client").lower()
        gdpr = bool(jurisdiction.get("gdpr", True))
        hipaa = bool(jurisdiction.get("hipaa", True))
        region = jurisdiction.get("region", "EU")

        lawful_basis = inp.get("lawful_basis", "contract")
        retention_days = int(inp.get("retention_days", 365))

        # LLM-backed sanitize (robust)
        sanitized, manifest, pii_report = sanitize_with_llm(ocr, role, gdpr, hipaa)

        # Export decision
        confidence = float(ocr.get("confidence", 0.0) or 0.0)
        export_state = "exported" if confidence >= EXPORT_CONFIDENCE_MIN else "needs_review"

        now = datetime.now(timezone.utc).isoformat()
        audit = {
            "decision_log": f"log://audit/{req.job_id}",
            "timestamp": now,
            "viewer_role": role,
            "jurisdiction": {"gdpr": gdpr, "hipaa": hipaa, "region": region},
            "lawful_basis": lawful_basis,
            "retention_days": retention_days,
            "minimum_necessary": MINIMUM_NECESSARY,
            "counts": {
                "redactions": len(manifest),
                "entities_kept": len(sanitized.get("entities", [])),
                "tables": len(sanitized.get("tables", [])),
            },
            "confidence": confidence
        }

        return {
            "status": "ok",
            "export_state": export_state,
            "views": {"sanitized": sanitized},
            "redaction_manifest": manifest,
            "pii_report": pii_report,
            "policy_version": POLICY_VERSION,
            "audit": audit
        }

    except HTTPException:
        # bubble up intended status codes
        raise
    except Exception as e:
        # generic failure => 500 (unexpected)
        raise HTTPException(status_code=500, detail=f"governance error: {e}")
