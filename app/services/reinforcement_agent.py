
import os
import re
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv



# ---------- Env + config (mirror ocr_agent.py) ----------
load_dotenv()

# ------------- MANUAL CONFIG (env wins only if manual placeholder left) -------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL")
# ------------------------------------------

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

# ---------- Gemini client shim (new 'google-genai' first, then legacy 'google-generativeai') ----------
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

# ---------------- FastAPI ----------------
class A2A(BaseModel):
    protocol: str
    intent: str
    job_id: str
    input: dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://suresightai.streamlit.app"],  # 👈 your Streamlit frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "ok": bool(API_KEY) and _client_mode in ("google-genai", "google-generativeai"),
        "service": "reinforcement",
        "sdk": _client_mode,
        "model": GEMINI_MODEL,
        "has_key": bool(API_KEY),
        "config_source": CONFIG_SOURCE,
    }

# ---------------- Helpers (mirror OCR style) ----------------
def _ensure_model_name(name: Optional[str]) -> str:
    aliases = {
        "gemini-2.5-flasj": "gemini-2.5-flash",
        "gemini-2.5-flahs": "gemini-2.5-flash",
        "gemini-1.5-flasj": "gemini-1.5-flash",
        "gemini-1.5-flahs": "gemini-1.5-flash",
    }
    s = (name or "").strip()
    return aliases.get(s, s) or "gemini-2.5-flash"

TOKEN_RE = re.compile(r"(?:\[REDACTED\])|(?:token:[a-z]+:[0-9a-f]{6,40})", re.IGNORECASE)

def _extract_tokens(text: str) -> List[str]:
    if not text:
        return []
    return list(dict.fromkeys(TOKEN_RE.findall(text)))

def _all_tokens_preserved(base_text: str, new_text: str) -> bool:
    base_tokens = _extract_tokens(base_text)
    if not base_tokens:
        return True
    return all(t in (new_text or "") for t in base_tokens)

def _extract_json_text_from_genai(resp: Any) -> str:
    # new SDK
    text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
    if text:
        return text.strip()
    try:
        cand = resp.candidates[0]
        for p in getattr(cand.content, "parts", []):
            t = getattr(p, "text", None)
            if t:
                return t.strip()
    except Exception:
        pass
    return ""

_CODEFENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"(\{.*\})", re.DOTALL)

def _parse_json_loosely(text: str) -> Dict[str, Any]:
    """
    Accepts JSON with/without code fences; tries to pull the largest JSON object.
    Raises ValueError if nothing parseable.
    """
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

def _normalize_view_shape(j: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal required keys; leave unknown keys on items untouched downstream
    return {
        "full_text": str(j.get("full_text", "") or ""),
        "entities": list(j.get("entities", []) or []),
        "tables": list(j.get("tables", []) or []),
    }

def _merge_entities(base: List[Dict[str, Any]], edited: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Merge LLM edits onto base while preserving extra keys (e.g., redacted).
    Strategy: index-aligned merge; if lengths differ, fall back to base for missing items.
    """
    if not edited:
        return base
    out: List[Dict[str, Any]] = []
    L = max(len(base), len(edited))
    for i in range(L):
        b = base[i] if i < len(base) else {}
        e = edited[i] if i < len(edited) else {}
        if not isinstance(b, dict):
            b = {}
        if not isinstance(e, dict):
            e = {}
        merged = dict(b)  # keep all base fields
        if "name" in e:       merged["name"] = e["name"]
        if "type" in e:       merged["type"] = e["type"]
        if "value" in e:      merged["value"] = e["value"]
        if "confidence" in e: merged["confidence"] = e["confidence"]
        # Preserve tokens
        if "value" in merged:
            if not _all_tokens_preserved(str(b.get("value","")), str(merged.get("value",""))):
                merged["value"] = b.get("value","")
        out.append(merged)
    return out

def _merge_tables(base: List[Dict[str, Any]], edited: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not edited:
        return base
    out: List[Dict[str, Any]] = []
    L = max(len(base), len(edited))
    for i in range(L):
        b = base[i] if i < len(base) else {}
        e = edited[i] if i < len(edited) else {}
        if not isinstance(b, dict):
            b = {}
        if not isinstance(e, dict):
            e = {}
        tid = e.get("id", b.get("id"))
        rows_e = e.get("rows")
        rows_b = b.get("rows")
        rows_final: List[List[str]] = []
        rows_src = rows_e if isinstance(rows_e, list) else rows_b if isinstance(rows_b, list) else []
        for r_idx, row in enumerate(rows_src):
            row = row if isinstance(row, (list, tuple)) else [row]
            base_row = rows_b[r_idx] if (isinstance(rows_b, list) and r_idx < len(rows_b)) else []
            new_row: List[str] = []
            for c_idx, cell in enumerate(row):
                new_txt = "" if cell is None else str(cell)
                base_txt = ""
                if isinstance(base_row, (list, tuple)) and c_idx < len(base_row):
                    base_txt = "" if base_row[c_idx] is None else str(base_row[c_idx])
                if not _all_tokens_preserved(base_txt, new_txt):
                    new_txt = base_txt
                new_row.append(new_txt)
            rows_final.append(new_row)
        out.append({"id": tid or b.get("id","table"), "rows": rows_final})
    return out

def _build_prompt(feedback: str, sanitized: Dict[str, Any], policy_version: Optional[str]) -> str:
    safe_json = json.dumps(sanitized, ensure_ascii=False)
    policy_note = f"(policy_version={policy_version})" if policy_version else ""

    fewshot_1_in = {
        "full_text": "Invoice Date: 12/03/24\nTerms of Instructions: Pay within 30 days.\nBody...",
        "entities": [{"name":"invoice_date","value":"12/03/24","type":"DATE","confidence":0.74}],
        "tables": []
    }
    fewshot_1_fb = "Normalize dates to YYYY-MM-DD. Put the 'Terms of Instructions' section above everything."
    fewshot_1_out = {
        "full_text": "Terms of Instructions: Pay within 30 days.\nInvoice Date: 2024-03-12\nBody...",
        "entities": [{"name":"invoice_date","value":"2024-03-12","type":"DATE","confidence":0.90}],
        "tables": []
    }

    return (
        "You are a STRICT EDITOR for a privacy-sanitized document view.\n"
        f"policy_context: {policy_note}\n\n"
        "INPUTS\n"
        "• sanitized_json: current sanitized view (already privacy-safe)\n"
        "• human_feedback: plain-English edit instructions\n\n"
        "RULES\n"
        "1) Output STRICT JSON ONLY with schema:\n"
        "{\n"
        '  "full_text": "<string>",\n'
        '  "entities": [ { "name": "<str>", "value": "<str>", "type": "<str>", "confidence": <number> }, ... ],\n'
        '  "tables": [ { "id": "<str>", "rows": [ [ "<str>", ... ], ... ] }, ... ]\n'
        "}\n"
        "2) NEVER unmask or alter \"[REDACTED]\" or strings like \"token:<type>:<hash>\".\n"
        "3) Do not invent PII/PHI; apply edits conservatively (date/currency normalization, ordering sections, header fixes, entity/type corrections, table shaping).\n"
        "4) If a requested change is ambiguous or would break privacy, leave that part unchanged.\n\n"
        "EXAMPLE\n"
        f"sanitized_json:\n{json.dumps(fewshot_1_in, ensure_ascii=False)}\n"
        f"human_feedback:\n{fewshot_1_fb}\n"
        f"correct_output:\n{json.dumps(fewshot_1_out, ensure_ascii=False)}\n\n"
        "=== YOUR TURN ===\n"
        f"sanitized_json:\n{safe_json}\n\n"
        f"human_feedback:\n{feedback or '(none)'}\n"
        "Return the EDITED JSON only."
    )

# ---------------- Endpoint ----------------
@app.post("/a2a/reinforce")
def reinforce_handler(req: A2A):
    if req.intent != "doc.reinforce":
        raise HTTPException(status_code=400, detail="intent must be 'doc.reinforce'")

    inp = req.input or {}
    apply_flag = bool(inp.get("apply", True))
    feedback = str(inp.get("feedback", "") or "")

    governance_result = inp.get("governance_result") or {}
    sanitized = inp.get("sanitized") or (governance_result.get("views", {}) or {}).get("sanitized")
    if not sanitized:
        raise HTTPException(status_code=400, detail="Missing sanitized input. Provide 'governance_result' or 'sanitized'.")

    policy_version = (governance_result or {}).get("policy_version")
    base_view = _normalize_view_shape(sanitized)

    # Fast path: user says don't apply
    if not apply_flag:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "status": "skipped",
            "used_governance": bool(governance_result),
            "final": base_view,
            "audit": {
                "timestamp": now,
                "job_id": req.job_id,
                "sdk": _client_mode,
                "model": GEMINI_MODEL,
                "latency_ms_total": 0,
                "applied_feedback": False,
                "policy_version": policy_version,
                "reason": "apply=false"
            }
        }

    if not API_KEY or _client_mode == "none":
        raise HTTPException(status_code=500, detail="Gemini not configured for Reinforcement agent")

    def _call_gemini_json(prompt: str) -> Tuple[Optional[Dict[str, Any]], str]:
        raw = ""
        if _client_mode == "google-genai":
            resp = _client.models.generate_content(  # type: ignore[attr-defined]
                model=_ensure_model_name(GEMINI_MODEL),
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json",
                    "max_output_tokens": 4096
                }
            )
            raw = _extract_json_text_from_genai(resp)
            if not raw:
                return None, ""
            try:
                return json.loads(raw), raw
            except Exception:
                return None, raw
        elif _client_mode == "google-generativeai":
            resp = _client.generate_content(  # type: ignore[attr-defined]
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                generation_config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json",
                    "max_output_tokens": 4096
                }
            )
            raw = getattr(resp, "text", None)
            if not raw:
                try:
                    cand = resp.candidates[0]
                    for p in cand.content.parts:
                        if getattr(p, "text", None):
                            raw = p.text
                            break
                except Exception:
                    pass
            if not raw:
                return None, ""
            try:
                return json.loads(raw), raw
            except Exception:
                return None, raw
        else:
            return None, ""

    t0 = time.time()
    raw_sample = ""
    try:
        prompt = _build_prompt(feedback, base_view, policy_version)

        # Try once
        llm_json, raw = _call_gemini_json(prompt)
        raw_sample = (raw or "")[:400]

        # Retry once if empty/invalid
        if llm_json is None:
            llm_json, raw2 = _call_gemini_json(prompt)
            if raw2:
                raw_sample = (raw2 or "")[:400]

        if llm_json is None:
            now = datetime.now(timezone.utc).isoformat()
            return {
                "status": "skipped",
                "used_governance": bool(governance_result),
                "final": base_view,
                "audit": {
                    "timestamp": now,
                    "job_id": req.job_id,
                    "sdk": _client_mode,
                    "model": GEMINI_MODEL,
                    "latency_ms_total": int((time.time() - t0) * 1000),
                    "applied_feedback": False,
                    "policy_version": policy_version,
                    "reason": "model_empty_or_invalid_json",
                    "raw_model_sample": raw_sample
                }
            }

        # Merge LLM output onto base (preserve extra keys and tokens)
        edited = _normalize_view_shape(llm_json)

        # full_text: accept if tokens preserved
        new_text = edited.get("full_text", base_view["full_text"])
        if not _all_tokens_preserved(base_view["full_text"], new_text):
            new_text = base_view["full_text"]

        # entities/tables merge
        merged_entities = _merge_entities(base_view["entities"], edited.get("entities"))
        merged_tables   = _merge_tables(base_view["tables"], edited.get("tables"))

        final_view = {
            "full_text": new_text,
            "entities": merged_entities,
            "tables": merged_tables,
        }

        # Was anything changed?
        applied = (
            final_view["full_text"] != base_view["full_text"] or
            json.dumps(final_view["entities"], separators=(",",":")) != json.dumps(base_view["entities"], separators=(",",":")) or
            json.dumps(final_view["tables"],   separators=(",",":")) != json.dumps(base_view["tables"],   separators=(",",":"))
        )

        now = datetime.now(timezone.utc).isoformat()
        return {
            "status": "ok",
            "used_governance": bool(governance_result),
            "final": final_view,
            "audit": {
                "timestamp": now,
                "job_id": req.job_id,
                "sdk": _client_mode,
                "model": GEMINI_MODEL,
                "latency_ms_total": int((time.time() - t0) * 1000),
                "applied_feedback": bool(applied),
                "policy_version": policy_version,
                "raw_model_sample": raw_sample
            }
        }

    except Exception as e:
        now = datetime.now(timezone.utc).isoformat()
        # Return 200 with status=error so the UI can display the reason without exploding
        return {
            "status": "error",
            "used_governance": bool(governance_result),
            "final": base_view,
            "audit": {
                "timestamp": now,
                "job_id": req.job_id,
                "sdk": _client_mode,
                "model": GEMINI_MODEL,
                "latency_ms_total": int((time.time() - t0) * 1000),
                "applied_feedback": False,
                "policy_version": policy_version,
                "reason": f"reinforcement exception: {e}"
            }
        }
