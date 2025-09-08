# app/services/reinforcement_agent.py
"""
Suresight AI — Reinforcement Agent (LLM-backed)
- Takes human feedback + (optionally) the Governance agent's sanitized output.
- If reinforcement is enabled, calls Gemini to apply feedback conservatively
  (never unmasking/redacting tokens), and returns STRICT JSON.
- If reinforcement is disabled, simply returns the Governance sanitized result as final.

Env / Manual config:
  MANUAL_GEMINI_API_KEY   -> hardcoded key (fallback to GEMINI_API_KEY / GOOGLE_API_KEY)
  MANUAL_GEMINI_MODEL     -> default "gemini-2.5-flash"

Endpoints:
  GET  /health
  POST /a2a/reinforce   (intent="doc.reinforce")

Input shape (POST /a2a/reinforce):
{
  "protocol": "a2a",
  "intent": "doc.reinforce",
  "job_id": "<id>",
  "input": {
    "apply": true,                         # if false, returns governance as-is
    "feedback": "User feedback text...",   # human feedback prompt (optional but recommended)
    "governance_result": { ... },          # full governance response (preferred)
    # OR instead of governance_result:
    "sanitized": { "full_text": "...", "entities": [...], "tables": [...] },

    # Optional: carry-through context for audit
    "viewer": {"role": "client"},          # not used for policy here; just recorded
    "jurisdiction": {"gdpr": true, "hipaa": true, "region": "EU"},
    "lawful_basis": "contract",
    "retention_days": 365
  }
}

Output shape:
{
  "status": "ok" | "skipped",
  "used_governance": true | false,
  "final": {
    "full_text": "...",
    "entities": [...],
    "tables": [...]
  },
  "audit": {
    "timestamp": "<ISO>",
    "job_id": "<id>",
    "sdk": "google-genai|google-generativeai|none",
    "model": "gemini-2.5-flash",
    "latency_ms_total": <int>,
    "applied_feedback": true|false,
    "policy_version": "<from governance if present>"
  }
}
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ------------- MANUAL CONFIG (env values take precedence only if manual placeholder left) -------------
MANUAL_GEMINI_API_KEY = os.getenv("MANUAL_GEMINI_API_KEY", "AIzaSyCi7XQTGOh_Nks15ap6sM1GWdCFVqcKQbo")
MANUAL_GEMINI_MODEL   = os.getenv("MANUAL_GEMINI_MODEL", "gemini-2.5-flash")
# ------------------------------------------------------------------------------------------------------

def _manual_key_set(v: str) -> bool:
    return bool(v) and not v.startswith("PASTE_") and not v.startswith("paste_")

API_KEY = MANUAL_GEMINI_API_KEY if _manual_key_set(MANUAL_GEMINI_API_KEY) else (
    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)
GEMINI_MODEL = MANUAL_GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CONFIG_SOURCE = "manual" if _manual_key_set(MANUAL_GEMINI_API_KEY) else (
    "env(GEMINI_API_KEY)" if os.getenv("GEMINI_API_KEY") else
    "env(GOOGLE_API_KEY)" if os.getenv("GOOGLE_API_KEY") else "none"
)

# ---------- Gemini client shim (prefer new google-genai, fallback to legacy google-generativeai) ----------
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

@app.get("/health")
def health():
    return {
        "ok": bool(API_KEY) and _client_mode in ("google-genai", "google-generativeai"),
        "service": "reinforcement",
        "sdk": _client_mode,
        "model": GEMINI_MODEL,
        "config_source": CONFIG_SOURCE,
    }

# ---------------- Helpers ----------------
def _ensure_model_name(name: str) -> str:
    aliases = {
        "gemini-2.5-flasj": "gemini-2.5-flash",
        "gemini-2.5-flahs": "gemini-2.5-flash",
        "gemini-1.5-flasj": "gemini-1.5-flash",
        "gemini-1.5-flahs": "gemini-1.5-flash",
    }
    fixed = aliases.get((name or "").strip(), (name or "").strip())
    return fixed or "gemini-2.5-flash"

def _extract_json_text_from_genai(resp: Any) -> str:
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

def _build_reinforcement_prompt(feedback: str, sanitized: Dict[str, Any], policy_version: Optional[str]) -> str:
    """
    Instructs the LLM to conservatively apply human feedback to the sanitized JSON.
    Emphasizes never unmasking tokens or fabricating PII.
    """
    safe_json = json.dumps(sanitized, ensure_ascii=False)
    policy_note = f"(policy_version={policy_version})" if policy_version else ""

    return (
        "You are a reinforcement assistant that refines a privacy-sanitized document view.\n"
        "INPUTS:\n"
        f"- policy_context: {policy_note}\n"
        "- sanitized_json: the current sanitized view from the Governance step.\n"
        "- human_feedback: user's instructions for improvements (formatting tweaks, entity/table fixes, doc structure).\n\n"
        "REQUIREMENTS:\n"
        "1) Return STRICT JSON ONLY. No markdown, no prose.\n"
        "2) Preserve privacy protections: never remove or alter redaction tokens like '[REDACTED]' or\n"
        "   pseudonym tokens of the form 'token:<type>:<hash>'. Do NOT introduce real PII/PHI.\n"
        "3) Apply feedback conservatively: fix labeling, grouping, minor text cleanups, table structure, or entity types/values\n"
        "   when clearly indicated by the feedback. If feedback conflicts with privacy constraints, ignore that portion.\n"
        "4) Output must follow EXACT schema:\n"
        "{\n"
        '  "full_text": "<string>",\n'
        '  "entities": [ { "name": "<str>", "value": "<str>", "type": "<str>", "confidence": <number> }, ... ],\n'
        '  "tables": [ { "id": "<str>", "rows": [ [ "<str>", ... ], ... ] }, ... ]\n'
        "}\n"
        "5) Keep values as strings; do not output nulls. If you remove an item, simply omit it.\n"
        "6) If you cannot safely apply a part of the feedback, leave the corresponding portion unchanged.\n\n"
        "sanitized_json:\n"
        f"{safe_json}\n\n"
        "human_feedback:\n"
        f"{feedback or '(none)'}\n"
    )

def _call_gemini_json(prompt: str) -> Dict[str, Any]:
    if _client_mode == "google-genai":
        resp = _client.models.generate_content(
            model=_ensure_model_name(GEMINI_MODEL),
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "max_output_tokens": 4096
            }
        )
        text = _extract_json_text_from_genai(resp)
        if not text:
            raise RuntimeError("Empty response from Gemini (google-genai)")
        return json.loads(text)

    elif _client_mode == "google-generativeai":
        resp = _client.generate_content(
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "max_output_tokens": 4096
            }
        )
        text = getattr(resp, "text", None)
        if not text:
            try:
                cand = resp.candidates[0]
                for p in cand.content.parts:
                    if getattr(p, "text", None):
                        text = p.text
                        break
            except Exception:
                pass
        if not text:
            raise RuntimeError("Empty response from Gemini (google-generativeai)")
        return json.loads(text)

    else:
        raise RuntimeError("Gemini client not initialized. Check API key and SDK installation.")

def _normalize_sanitized_shape(j: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the output has the expected sanitized schema.
    """
    return {
        "full_text": str(j.get("full_text", "") or ""),
        "entities": list(j.get("entities", []) or []),
        "tables": list(j.get("tables", []) or []),
    }

def _extract_sanitized_from_governance(gov: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        return gov.get("views", {}).get("sanitized") or None
    except Exception:
        return None

# ---------------- Endpoint ----------------
@app.post("/a2a/reinforce")
def reinforce_handler(req: A2A):
    if req.intent != "doc.reinforce":
        raise HTTPException(status_code=400, detail="intent must be 'doc.reinforce'")

    inp = req.input or {}
    apply_flag = bool(inp.get("apply", True))
    feedback = str(inp.get("feedback", "") or "")

    # Prefer full governance_result; accept direct sanitized fallback
    governance_result = inp.get("governance_result") or {}
    sanitized = inp.get("sanitized") or _extract_sanitized_from_governance(governance_result)

    if not sanitized:
        raise HTTPException(
            status_code=400,
            detail="Missing sanitized input. Provide 'governance_result' (preferred) or 'sanitized' object."
        )

    policy_version = (governance_result or {}).get("policy_version")

    # If caller decided not to apply reinforcement, return pass-through
    if not apply_flag:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "status": "skipped",
            "used_governance": bool(governance_result),
            "final": _normalize_sanitized_shape(sanitized),
            "audit": {
                "timestamp": now,
                "job_id": req.job_id,
                "sdk": _client_mode,
                "model": GEMINI_MODEL,
                "latency_ms_total": 0,
                "applied_feedback": False,
                "policy_version": policy_version
            }
        }

    if not API_KEY or _client_mode == "none":
        raise HTTPException(
            status_code=500,
            detail="Gemini not configured for Reinforcement agent (no API key or SDK). Set MANUAL_GEMINI_API_KEY or env key and restart."
        )

    # Apply reinforcement with LLM
    t0 = time.time()
    try:
        prompt = _build_reinforcement_prompt(feedback, _normalize_sanitized_shape(sanitized), policy_version)
        llm_json = _call_gemini_json(prompt)
        final_view = _normalize_sanitized_shape(llm_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"reinforcement error: {e}")

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
            "applied_feedback": True,
            "policy_version": policy_version
        }
    }
