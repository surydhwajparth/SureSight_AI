# # app/services/ocr_agent.py
# """
# Suresight AI — OCR Agent (Gemini, manual key)
# - Uses a MANUAL API KEY and MODEL NAME (hardcoded below). Falls back to env vars only if the
#   manual key placeholder isn't replaced.
# - Accepts A2A requests with page images (base64) or HTTP(S) URLs.
# - Calls Google Gemini (2.5 Flash by default) to extract:
#   full_text, entities[{name,value,type,confidence}], tables, doc_class, confidence.
# """

# import os
# import json
# import time
# import base64
# from typing import List, Dict, Any, Optional

# import httpx
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# # ========= MANUAL CONFIG (edit these two lines) =========
# GEMINI_API_KEY = "AIzaSyCi7XQTGOh_Nks15ap6sM1GWdCFVqcKQbo"   # <-- put your real Gemini API key
# GEMINI_MODEL   = "gemini-2.5-flash"             # e.g., "gemini-2.5-flash" or "gemini-1.5-flash"
# # ========================================================

# # If you leave the placeholder, we fall back to env vars so devs can still run with .env
# def _manual_key_set(v: str) -> bool:
#     return bool(v) and not v.startswith("PASTE_") and not v.startswith("paste_")

# API_KEY = GEMINI_API_KEY if _manual_key_set(GEMINI_API_KEY) else (
#     os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
# )
# GEMINI_MODEL = GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# CONFIG_SOURCE = "manual" if _manual_key_set(GEMINI_API_KEY) else (
#     "env(GEMINI_API_KEY)" if os.getenv("GEMINI_API_KEY") else
#     "env(GOOGLE_API_KEY)" if os.getenv("GOOGLE_API_KEY") else "none"
# )

# # ---------- Gemini client shim (new 'google-genai' first, then legacy 'google-generativeai') ----------
# _client_mode: Optional[str] = None
# _client = None
# try:
#     # New SDK
#     from google import genai as ggenai  # type: ignore
#     if not API_KEY:
#         raise RuntimeError("Missing API key for google-genai")
#     _client = ggenai.Client(api_key=API_KEY)
#     _client_mode = "google-genai"
# except Exception:
#     try:
#         # Legacy SDK
#         import google.generativeai as ggenai  # type: ignore
#         if not API_KEY:
#             raise RuntimeError("Missing API key for google-generativeai")
#         ggenai.configure(api_key=API_KEY)
#         _client = ggenai.GenerativeModel(GEMINI_MODEL)
#         _client_mode = "google-generativeai"
#     except Exception:
#         _client_mode = "none"


# # ---------- FastAPI wiring ----------
# class A2A(BaseModel):
#     protocol: str
#     intent: str
#     job_id: str
#     input: dict


# app = FastAPI()


# @app.get("/health")
# def health():
#     """Non-secret status to help debug configuration."""
#     return {
#         "ok": bool(API_KEY) and _client_mode in ("google-genai", "google-generativeai"),
#         "service": "ocr",
#         "sdk": _client_mode,
#         "model": GEMINI_MODEL,
#         "has_key": bool(API_KEY),
#         "config_source": CONFIG_SOURCE,
#     }


# # ---------- Helpers ----------
# def _ensure_model_name(name: str) -> str:
#     return name or "gemini-1.5-flash"


# def _b64_from_bytes(b: bytes) -> str:
#     return base64.b64encode(b).decode("utf-8")


# async def _fetch_bytes(url: str) -> bytes:
#     """
#     Fetch bytes for HTTP(S) URLs. For gs:// or file://, raise a helpful error.
#     """
#     if url.startswith("gs://"):
#         raise HTTPException(
#             status_code=400,
#             detail="gs:// fetching not implemented in this demo. Pass page_images_b64 or presigned HTTPS URLs."
#         )
#     if url.startswith("file://"):
#         raise HTTPException(
#             status_code=400,
#             detail="file:// is not supported by the service. Please upload bytes via the UI."
#         )
#     async with httpx.AsyncClient(timeout=60) as cli:
#         r = await cli.get(url)
#         r.raise_for_status()
#         return r.content


# def _extract_json_text_from_genai(resp: Any) -> str:
#     """
#     Try hard to extract JSON text from google-genai response.
#     """
#     text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
#     if text:
#         return text.strip()

#     # Fallback: try candidates->content->parts
#     try:
#         cand = resp.candidates[0]
#         for p in getattr(cand.content, "parts", []):
#             t = getattr(p, "text", None)
#             if t:
#                 return t.strip()
#     except Exception:
#         pass
#     return ""


# def _normalize_result(j: Dict[str, Any], num_pages: int) -> Dict[str, Any]:
#     return {
#         "full_text": j.get("full_text", "") or "",
#         "entities": j.get("entities", []) or [],
#         "tables": j.get("tables", []) or [],
#         "doc_class": j.get("doc_class", "unknown") or "unknown",
#         "confidence": float(j.get("confidence", 0.0) or 0.0),
#         "page_metrics": [{"p": i + 1, "latency_ms": None} for i in range(max(1, num_pages))],
#     }


# def _build_system_prompt() -> str:
#     return (
#         "You are a precise document understanding engine.\n"
#         "Extract strictly JSON with keys:\n"
#         "  full_text: string (all text on the page(s)),\n"
#         "  entities: array of {name, value, type, confidence},\n"
#         "  tables: array of {id, rows: array of arrays of strings},\n"
#         "  doc_class: string (e.g., invoice, receipt, id, form, letter, clinical_note),\n"
#         "  confidence: number in [0,1] (overall extraction confidence).\n"
#         "Do not output narration or markdown. JSON only."
#     )


# def _build_user_parts(images_b64: List[str]) -> List[Dict[str, Any]]:
#     parts: List[Dict[str, Any]] = []
#     for b64 in images_b64:
#         parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})
#     parts.append({"text": "Return JSON only. Do not include prose outside JSON."})
#     return parts


# def _gemini_call_json(images_b64: List[str]) -> Dict[str, Any]:
#     """
#     Call Gemini via whichever SDK is available and return parsed JSON dict.
#     """
#     if _client_mode == "google-genai":
#         system_prompt = _build_system_prompt()
#         parts = _build_user_parts(images_b64)

#         resp = _client.models.generate_content(
#             model=_ensure_model_name(GEMINI_MODEL),
#             contents=[
#                 {
#                     "role": "user",
#                     "parts": [
#                         {"text": system_prompt},
#                         *parts
#                     ]
#                 }
#             ],
#             config={
#                 "temperature": 0.2,
#                 "response_mime_type": "application/json",
#                 "max_output_tokens": 4096
#             }
#         )
#         text = _extract_json_text_from_genai(resp)
#         if not text:
#             raise RuntimeError("Empty response from Gemini (google-genai)")
#         return json.loads(text)

#     elif _client_mode == "google-generativeai":
#         # Legacy SDK
#         system_prompt = _build_system_prompt()
#         parts = _build_user_parts(images_b64)

#         resp = _client.generate_content(
#             contents=[
#                 {"role": "system", "parts": [{"text": system_prompt}]},
#                 {"role": "user",   "parts": parts},
#             ],
#             generation_config={
#                 "temperature": 0.2,
#                 "response_mime_type": "application/json",
#                 "max_output_tokens": 4096
#             }
#         )
#         text = getattr(resp, "text", None)
#         if not text:
#             # one more fallback attempt
#             try:
#                 cand = resp.candidates[0]
#                 for p in cand.content.parts:
#                     if hasattr(p, "text") and p.text:
#                         text = p.text
#                         break
#             except Exception:
#                 pass
#         if not text:
#             raise RuntimeError("Empty response from Gemini (google-generativeai)")
#         return json.loads(text)

#     else:
#         raise RuntimeError("Gemini client not initialized. Check API key and SDK installation.")


# # ---------- Main endpoint ----------
# @app.post("/a2a/ocr")
# async def ocr_handler(req: A2A):
#     if req.intent != "doc.extract":
#         raise HTTPException(status_code=400, detail="intent must be 'doc.extract'")

#     if not API_KEY or _client_mode == "none":
#         raise HTTPException(
#             status_code=500,
#             detail="Gemini not configured (no API key or SDK). Set GEMINI_API_KEY in the file or env key and restart."
#         )
#     else:
#         print("Gemini client initialized.")

#     inp = req.input or {}
#     images_b64: List[str] = inp.get("page_images_b64", [])
#     pages: List[str] = inp.get("pages", [])

#     # If URLs provided, try to fetch as bytes (HTTP/HTTPS only), else require base64 images.
#     if not images_b64 and pages:
#         fetched: List[str] = []
#         for url in pages:
#             data = await _fetch_bytes(url)  # raises for gs:// etc (see helper)
#             fetched.append(_b64_from_bytes(data))
#         images_b64 = fetched

#     if not images_b64:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide 'page_images_b64' (recommended) or HTTP(S) 'pages'."
#         )

#     t0 = time.time()
#     try:
#         j = _gemini_call_json(images_b64)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

#     result = _normalize_result(j, num_pages=len(images_b64))
#     result["latency_ms_total"] = int((time.time() - t0) * 1000)
#     return result

# app/services/ocr_agent.py
"""
Suresight AI — OCR Agent (Gemini, manual key)
- Uses a MANUAL API KEY and MODEL NAME (hardcoded below). Falls back to env vars only if the
  manual key placeholder isn't replaced.
- Accepts A2A requests with page images (base64) or HTTP(S) URLs.
- Calls Google Gemini (2.5 Flash by default) to extract:
  full_text, entities[{name,value,type,confidence}], tables, doc_class, confidence.

Fixes:
- MIME sniffing per image so JPEGs don’t get mislabeled as PNG (which caused random 500s).
- Robust JSON extraction (handles code fences / extra text).
- Retry-on-failure/backoff to reduce transient “internal server error” from the model.
"""

import os
import json
import time
import base64
import re
from typing import List, Dict, Any, Optional, Tuple

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

# ------------- MANUAL CONFIG (env wins only if manual placeholder left) -------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL")
# ------------------------------------------           # e.g., "gemini-2.5-flash" or "gemini-1.5-flash"
# ========================================================

# If you leave the placeholder, we fall back to env vars so devs can still run with .env
def _manual_key_set(v: str) -> bool:
    return bool(v) and not v.startswith("PASTE_") and not v.startswith("paste_")

API_KEY = GEMINI_API_KEY if _manual_key_set(GEMINI_API_KEY) else (
    os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)
GEMINI_MODEL = GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
CONFIG_SOURCE = "manual" if _manual_key_set(GEMINI_API_KEY) else (
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


# ---------- FastAPI wiring ----------
class A2A(BaseModel):
    protocol: str
    intent: str
    job_id: str
    input: dict


app = FastAPI()


@app.get("/health")
def health():
    """Non-secret status to help debug configuration."""
    return {
        "ok": bool(API_KEY) and _client_mode in ("google-genai", "google-generativeai"),
        "service": "ocr",
        "sdk": _client_mode,
        "model": GEMINI_MODEL,
        "has_key": bool(API_KEY),
        "config_source": CONFIG_SOURCE,
    }


# ---------- Helpers ----------
def _ensure_model_name(name: str) -> str:
    return name or "gemini-1.5-flash"


def _b64_from_bytes(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


async def _fetch_bytes(url: str) -> bytes:
    """
    Fetch bytes for HTTP(S) URLs. For gs:// or file://, raise a helpful error.
    """
    if url.startswith("gs://"):
        raise HTTPException(
            status_code=400,
            detail="gs:// fetching not implemented in this demo. Pass page_images_b64 or presigned HTTPS URLs."
        )
    if url.startswith("file://"):
        raise HTTPException(
            status_code=400,
            detail="file:// is not supported by the service. Please upload bytes via the UI."
        )
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.get(url)
        r.raise_for_status()
        return r.content


def _guess_image_mime(b: bytes) -> str:
    # PNG magic: \x89PNG\r\n\x1a\n
    if b.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    # JPEG magic: \xFF\xD8\xFF
    if b.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    # GIF magic (rare but safe): GIF87a / GIF89a
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return "application/octet-stream"


def _guess_image_mime_from_b64(b64: str) -> str:
    try:
        raw = base64.b64decode(b64, validate=False)
    except Exception:
        return "application/octet-stream"
    return _guess_image_mime(raw)


def _extract_json_text_from_genai(resp: Any) -> str:
    """
    Try hard to extract JSON text from google-genai response.
    """
    text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
    if text:
        return text.strip()

    # Fallback: try candidates->content->parts
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

    # Direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try ```json ... ```
    m = _CODEFENCE_RE.search(text)
    if m:
        inner = m.group(1)
        try:
            return json.loads(inner)
        except Exception:
            pass

    # Fallback: grab the largest {...} block
    objs = _JSON_OBJECT_RE.findall(text)
    if objs:
        # pick the longest candidate
        candidate = max(objs, key=len)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("no valid JSON object found")


def _normalize_result(j: Dict[str, Any], num_pages: int) -> Dict[str, Any]:
    return {
        "full_text": j.get("full_text", "") or "",
        "entities": j.get("entities", []) or [],
        "tables": j.get("tables", []) or [],
        "doc_class": j.get("doc_class", "unknown") or "unknown",
        "confidence": float(j.get("confidence", 0.0) or 0.0),
        "page_metrics": [{"p": i + 1, "latency_ms": None} for i in range(max(1, num_pages))],
    }


def _build_system_prompt() -> str:
    return (
        "You are a precise document understanding engine.\n"
        "Extract strictly JSON with keys:\n"
        "  full_text: string (all text on the page(s)),\n"
        "  entities: array of {name, value, type, confidence},\n"
        "  tables: array of {id, rows: array of arrays of strings},\n"
        "  doc_class: string (e.g., invoice, receipt, id, form, letter, clinical_note),\n"
        "  confidence: number in [0,1] (overall extraction confidence).\n"
        "Do not output narration or markdown. JSON only."
    )


def _build_user_parts_with_mime(images_b64: List[str]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    for b64 in images_b64:
        mime = _guess_image_mime_from_b64(b64)
        # For safety: if we couldn't guess, default to image/jpeg (most uploads)
        if mime == "application/octet-stream":
            mime = "image/jpeg"
        parts.append({"inline_data": {"mime_type": mime, "data": b64}})
    parts.append({"text": "Return JSON only. Do not include prose outside JSON."})
    return parts


def _gemini_call_json_once(images_b64: List[str]) -> Dict[str, Any]:
    """
    Call Gemini via whichever SDK is available and return parsed JSON dict.
    Single attempt (no retry here).
    """
    if _client_mode == "google-genai":
        system_prompt = _build_system_prompt()
        parts = _build_user_parts_with_mime(images_b64)

        resp = _client.models.generate_content(
            model=_ensure_model_name(GEMINI_MODEL),
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt},
                        *parts
                    ]
                }
            ],
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "max_output_tokens": 3072
            }
        )
        raw_text = _extract_json_text_from_genai(resp)
        if not raw_text:
            raise RuntimeError("Empty response from Gemini (google-genai)")

        return _parse_json_loosely(raw_text)

    elif _client_mode == "google-generativeai":
        # Legacy SDK
        system_prompt = _build_system_prompt()
        parts = _build_user_parts_with_mime(images_b64)

        resp = _client.generate_content(
            contents=[
                {"role": "system", "parts": [{"text": system_prompt}]},
                {"role": "user",   "parts": parts},
            ],
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "max_output_tokens": 3072
            }
        )
        # grab text robustly
        text = getattr(resp, "text", None)
        if not text:
            try:
                cand = resp.candidates[0]
                for p in cand.content.parts:
                    if hasattr(p, "text") and p.text:
                        text = p.text
                        break
            except Exception:
                pass
        if not text:
            raise RuntimeError("Empty response from Gemini (google-generativeai)")

        return _parse_json_loosely(text)

    else:
        raise RuntimeError("Gemini client not initialized. Check API key and SDK installation.")


def _gemini_call_json_with_retry(images_b64: List[str], attempts: int = 2, backoff_base: float = 0.6) -> Dict[str, Any]:
    last_err: Optional[Exception] = None
    for i in range(attempts):
        try:
            return _gemini_call_json_once(images_b64)
        except Exception as e:
            last_err = e
            # transient backoff (handles 429/503/parse flukes)
            time.sleep(backoff_base * (i + 1))
    # exhaust
    raise last_err if last_err else RuntimeError("Unknown OCR error")


# ---------- Main endpoint ----------
@app.post("/a2a/ocr")
async def ocr_handler(req: A2A):
    if req.intent != "doc.extract":
        raise HTTPException(status_code=400, detail="intent must be 'doc.extract'")

    if not API_KEY or _client_mode == "none":
        raise HTTPException(
            status_code=500,
            detail="Gemini not configured (no API key or SDK). Set GEMINI_API_KEY in the file or env key and restart."
        )
    else:
        print("Gemini client initialized.")

    inp = req.input or {}
    images_b64: List[str] = inp.get("page_images_b64", []) or []
    pages: List[str] = inp.get("pages", []) or []

    # If URLs provided, try to fetch as bytes (HTTP/HTTPS only), else require base64 images.
    if not images_b64 and pages:
        fetched: List[str] = []
        for url in pages:
            data = await _fetch_bytes(url)  # raises for gs:// etc (see helper)
            fetched.append(_b64_from_bytes(data))
        images_b64 = fetched

    # Clean/validate inputs (filter empties / non-strings)
    images_b64 = [b for b in images_b64 if isinstance(b, str) and b.strip()]
    if not images_b64:
        raise HTTPException(
            status_code=400,
            detail="Provide 'page_images_b64' (recommended) or HTTP(S) 'pages'."
        )

    # Optional: locale hints are accepted but not required
    # locale = ((inp.get("hints") or {}).get("locale")) or "en-IN"

    t0 = time.time()
    try:
        j = _gemini_call_json_with_retry(images_b64, attempts=2, backoff_base=0.6)
    except Exception as e:
        # Keep it explicit for the UI
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    result = _normalize_result(j, num_pages=len(images_b64))
    result["latency_ms_total"] = int((time.time() - t0) * 1000)

    # If everything came back empty, make that explicit (helps UI debugging instead of “no context” mystery)
    if not (result["full_text"] or result["entities"] or result["tables"]):
        # surface as 502 so the caller can decide to retry or skip this file
        raise HTTPException(status_code=502, detail="OCR produced no extractable content")

    return result
