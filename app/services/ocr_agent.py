# app/services/ocr_agent.py
"""
Suresight AI — OCR Agent (Gemini, manual key)
- Uses a MANUAL API KEY and MODEL NAME (hardcoded below). Falls back to env vars only if the
  manual key placeholder isn't replaced.
- Accepts A2A requests with page images (base64) or HTTP(S) URLs.
- Calls Google Gemini (2.5 Flash by default) to extract:
  full_text, entities[{name,value,type,confidence}], tables, doc_class, confidence.
"""

import os
import json
import time
import base64
from typing import List, Dict, Any, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ========= MANUAL CONFIG (edit these two lines) =========
MANUAL_GEMINI_API_KEY = "AIzaSyCi7XQTGOh_Nks15ap6sM1GWdCFVqcKQbo"   # <-- put your real Gemini API key
MANUAL_GEMINI_MODEL   = "gemini-2.5-flash"             # e.g., "gemini-2.5-flash" or "gemini-1.5-flash"
# ========================================================

# If you leave the placeholder, we fall back to env vars so devs can still run with .env
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


def _build_user_parts(images_b64: List[str]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    for b64 in images_b64:
        parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})
    parts.append({"text": "Return JSON only. Do not include prose outside JSON."})
    return parts


def _gemini_call_json(images_b64: List[str]) -> Dict[str, Any]:
    """
    Call Gemini via whichever SDK is available and return parsed JSON dict.
    """
    if _client_mode == "google-genai":
        system_prompt = _build_system_prompt()
        parts = _build_user_parts(images_b64)

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
                "max_output_tokens": 4096
            }
        )
        text = _extract_json_text_from_genai(resp)
        if not text:
            raise RuntimeError("Empty response from Gemini (google-genai)")
        return json.loads(text)

    elif _client_mode == "google-generativeai":
        # Legacy SDK
        system_prompt = _build_system_prompt()
        parts = _build_user_parts(images_b64)

        resp = _client.generate_content(
            contents=[
                {"role": "system", "parts": [{"text": system_prompt}]},
                {"role": "user",   "parts": parts},
            ],
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "max_output_tokens": 4096
            }
        )
        text = getattr(resp, "text", None)
        if not text:
            # one more fallback attempt
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
        return json.loads(text)

    else:
        raise RuntimeError("Gemini client not initialized. Check API key and SDK installation.")


# ---------- Main endpoint ----------
@app.post("/a2a/ocr")
async def ocr_handler(req: A2A):
    if req.intent != "doc.extract":
        raise HTTPException(status_code=400, detail="intent must be 'doc.extract'")

    if not API_KEY or _client_mode == "none":
        raise HTTPException(
            status_code=500,
            detail="Gemini not configured (no API key or SDK). Set MANUAL_GEMINI_API_KEY in the file or env key and restart."
        )
    else:
        print("Gemini client initialized.")

    inp = req.input or {}
    images_b64: List[str] = inp.get("page_images_b64", [])
    pages: List[str] = inp.get("pages", [])

    # If URLs provided, try to fetch as bytes (HTTP/HTTPS only), else require base64 images.
    if not images_b64 and pages:
        fetched: List[str] = []
        for url in pages:
            data = await _fetch_bytes(url)  # raises for gs:// etc (see helper)
            fetched.append(_b64_from_bytes(data))
        images_b64 = fetched

    if not images_b64:
        raise HTTPException(
            status_code=400,
            detail="Provide 'page_images_b64' (recommended) or HTTP(S) 'pages'."
        )

    t0 = time.time()
    try:
        j = _gemini_call_json(images_b64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

    result = _normalize_result(j, num_pages=len(images_b64))
    result["latency_ms_total"] = int((time.time() - t0) * 1000)
    return result

# ##################################ORIGINAL FILE ENDS HERE##################################


# app/services/ocr_agent.py
# """
# Suresight AI — OCR Agent (Gemini) with PDF + Image support

# Inputs (req.input):
#   - page_images_b64: [base64 PNG/JPG]
#   - pages:           [HTTP/HTTPS URLs to images or PDFs]  (auto-detected)
#   - pdfs:            [HTTP/HTTPS URLs to PDFs]
#   - pdfs_b64:        [base64 PDFs]
#   - pdf_page_limit:  int (optional, cap pages per PDF)
#   - pdf_dpi:         int (optional, render DPI for legacy fallback)

# Behavior:
#   - New SDK (google-genai): PDFs/images are sent as bytes via types.Part.from_bytes.
#   - Legacy SDK (google-generativeai): PDFs are rendered to PNG with PyMuPDF (if available).
# Output:
#   JSON with full_text, entities, tables, doc_class, confidence, etc.
# """

# import os
# import json
# import time
# import base64
# from typing import List, Dict, Any, Optional, Tuple

# import httpx
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel

# # ========= MANUAL CONFIG (edit as needed) =========
# MANUAL_GEMINI_API_KEY = "AIzaSyCi7XQTGOh_Nks15ap6sM1GWdCFVqcKQbo"  # ⚠️ use env vars in prod
# MANUAL_GEMINI_MODEL   = "gemini-2.5-flash"           # e.g., "gemini-2.5-flash"
# # ==================================================

# def _manual_key_set(v: str) -> bool:
#     return bool(v) and not v.lower().startswith("paste_")

# API_KEY = MANUAL_GEMINI_API_KEY if _manual_key_set(MANUAL_GEMINI_API_KEY) else (
#     os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
# )
# GEMINI_MODEL = MANUAL_GEMINI_MODEL or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# CONFIG_SOURCE = "manual" if _manual_key_set(MANUAL_GEMINI_API_KEY) else (
#     "env(GEMINI_API_KEY)" if os.getenv("GEMINI_API_KEY") else
#     "env(GOOGLE_API_KEY)" if os.getenv("GOOGLE_API_KEY") else "none"
# )

# # ---------- Gemini client shim ----------
# _client_mode: Optional[str] = None
# _client = None
# try:
#     # New SDK
#     from google import genai as ggenai  # type: ignore
#     from google.genai import types as gtypes  # type: ignore
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

# # ---------- Optional PDF rendering for legacy fallback ----------
# try:
#     import fitz  # PyMuPDF
#     _pdf_ok = True
# except Exception:
#     _pdf_ok = False

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
#         "pdf_support": (_client_mode == "google-genai") or _pdf_ok,
#     }

# # ---------- Helpers ----------
# def _ensure_model_name(name: str) -> str:
#     return name or "gemini-2.5-flash"

# def _b64_from_bytes(b: bytes) -> str:
#     return base64.b64encode(b).decode("utf-8")

# def _is_pdf_bytes(b: bytes) -> bool:
#     return len(b) >= 5 and b[:5] == b"%PDF-"

# def _is_pdf_content_type(ct: Optional[str]) -> bool:
#     return bool(ct) and "pdf" in ct.lower()

# def _guess_image_mime(b: bytes) -> str:
#     if b.startswith(b"\x89PNG\r\n\x1a\n"): return "image/png"
#     if b.startswith(b"\xff\xd8\xff"): return "image/jpeg"
#     return "application/octet-stream"

# async def _fetch_bytes(url: str) -> Tuple[bytes, Optional[str]]:
#     """
#     Fetch bytes + content-type for HTTP(S) URLs. For gs:// or file://, raise helpful error.
#     """
#     if url.startswith("gs://"):
#         raise HTTPException(
#             status_code=400,
#             detail="gs:// not implemented. Pass page_images_b64/pdfs_b64 or presigned HTTPS URLs."
#         )
#     if url.startswith("file://"):
#         raise HTTPException(
#             status_code=400,
#             detail="file:// is not supported. Upload bytes via the UI."
#         )
#     async with httpx.AsyncClient(timeout=60) as cli:
#         r = await cli.get(url)
#         r.raise_for_status()
#         return r.content, r.headers.get("content-type")

# def _pdf_to_images_b64(pdf_bytes: bytes, page_limit: Optional[int] = None, dpi: int = 180) -> List[str]:
#     """
#     Render PDF pages to PNG (base64) using PyMuPDF. Legacy-only fallback.
#     """
#     if not _pdf_ok:
#         raise HTTPException(status_code=500, detail="PDF rendering unavailable (install 'pymupdf').")
#     try:
#         doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid PDF: {e}")

#     images: List[str] = []
#     try:
#         n = doc.page_count
#         max_pages = min(n, page_limit) if page_limit else n
#         zoom = dpi / 72.0
#         mat = fitz.Matrix(zoom, zoom)
#         for i in range(max_pages):
#             page = doc.load_page(i)
#             pix = page.get_pixmap(matrix=mat, alpha=False)
#             images.append(_b64_from_bytes(pix.tobytes("png")))
#     finally:
#         doc.close()
#     if not images:
#         raise HTTPException(status_code=400, detail="PDF contained no renderable pages.")
#     return images

# def _extract_json_text_from_genai(resp: Any) -> str:
#     """
#     Try hard to extract JSON text from google(-)genai response.
#     """
#     text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
#     if text:
#         return text.strip()
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

# # ---------- Input ingestion ----------
# async def _gather_media_bytes(inp: Dict[str, Any]) -> List[Tuple[bytes, str]]:
#     """
#     Returns [(bytes, mime)] from all supported inputs.
#     - page_images_b64: PNG/JPG assumed (mime sniffed)
#     - pages: URLs to images or PDFs (auto-detect)
#     - pdfs: URLs to PDFs
#     - pdfs_b64: base64 PDFs
#     """
#     media: List[Tuple[bytes, str]] = []

#     # page_images_b64 (assume image)
#     for b64 in inp.get("page_images_b64", []) or []:
#         raw = base64.b64decode(b64, validate=True)
#         media.append((raw, _guess_image_mime(raw)))

#     # pages (URLs -> image or PDF)
#     for url in inp.get("pages", []) or []:
#         raw, ctype = await _fetch_bytes(url)
#         if _is_pdf_bytes(raw) or _is_pdf_content_type(ctype):
#             media.append((raw, "application/pdf"))
#         else:
#             media.append((raw, _guess_image_mime(raw)))

#     # pdfs (URLs to PDFs)
#     for url in inp.get("pdfs", []) or []:
#         raw, _ = await _fetch_bytes(url)
#         if not _is_pdf_bytes(raw):
#             raise HTTPException(status_code=400, detail=f"URL is not a PDF: {url}")
#         media.append((raw, "application/pdf"))

#     # pdfs_b64 (base64 PDFs)
#     for b64 in inp.get("pdfs_b64", []) or []:
#         raw = base64.b64decode(b64, validate=True)
#         if not _is_pdf_bytes(raw):
#             raise HTTPException(status_code=400, detail="An item in 'pdfs_b64' is not a PDF.")
#         media.append((raw, "application/pdf"))

#     return media

# # ---------- Gemini calls ----------
# async def _gemini_call_json(inp: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     New SDK: push PDFs/images as bytes via types.Part.
#     Legacy SDK: convert PDFs -> PNG (via PyMuPDF) and push images as inline_data.
#     """
#     system_prompt = _build_system_prompt()

#     if _client_mode == "google-genai":
#         # Build parts directly from raw media
#         media = await _gather_media_bytes(inp)
#         if not media:
#             raise HTTPException(status_code=400, detail="Provide 'page_images_b64', 'pages', 'pdfs', or 'pdfs_b64'.")

#         parts: List[Any] = []
#         for raw, mime in media:
#             parts.append(gtypes.Part.from_bytes(data=raw, mime_type=mime))

#         resp = _client.models.generate_content(
#             model=_ensure_model_name(GEMINI_MODEL),
#             contents=[
#                 {"role": "user", "parts": [{"text": system_prompt}, *parts, {"text": "Return JSON only."}]}
#             ],
#             config={
#                 "temperature": 0.2,
#                 "response_mime_type": "application/json",
#                 "max_output_tokens": 4096,
#             },
#         )
#         text = _extract_json_text_from_genai(resp)
#         if not text:
#             raise RuntimeError("Empty response from Gemini (google-genai)")
#         return json.loads(text)

#     elif _client_mode == "google-generativeai":
#         # Legacy SDK expects images. If PDFs present, render to images.
#         # 1) Gather media
#         media = await _gather_media_bytes(inp)
#         images_b64: List[str] = []

#         # 2) Expand PDFs to images; keep images as-is
#         page_limit = inp.get("pdf_page_limit")
#         page_limit = page_limit if isinstance(page_limit, int) and page_limit > 0 else None
#         dpi = int(inp.get("pdf_dpi", 180))

#         for raw, mime in media:
#             if mime == "application/pdf":
#                 if not _pdf_ok:
#                     raise HTTPException(status_code=500, detail="PDF provided but 'pymupdf' not installed for legacy SDK.")
#                 images_b64.extend(_pdf_to_images_b64(raw, page_limit=page_limit, dpi=dpi))
#             else:
#                 # If user sent raw bytes (not base64), we still need base64 for inline_data
#                 images_b64.append(_b64_from_bytes(raw))

#         if not images_b64:
#             raise HTTPException(status_code=400, detail="No renderable images found from inputs.")

#         # 3) Build request in legacy format (inline_data image/png; PNG vs JPEG doesn't matter to Gemini)
#         parts = []
#         for b64 in images_b64:
#             parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})
#         parts.append({"text": "Return JSON only. Do not include prose outside JSON."})

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
#             try:
#                 cand = resp.candidates[0]
#                 for p in cand.content.parts:
#                     if getattr(p, "text", None):
#                         text = p.text
#                         break
#             except Exception:
#                 pass
#         if not text:
#             raise RuntimeError("Empty response from Gemini (google-generativeai)")
#         return json.loads(text)

#     else:
#         raise HTTPException(status_code=500, detail="Gemini client not initialized. Check API key and SDK installation.")

# # ---------- Main endpoint ----------
# @app.post("/a2a/ocr")
# async def ocr_handler(req: A2A):
#     if req.intent != "doc.extract":
#         raise HTTPException(status_code=400, detail="intent must be 'doc.extract'")

#     if not API_KEY or _client_mode == "none":
#         raise HTTPException(
#             status_code=500,
#             detail="Gemini not configured (no API key or SDK). Set MANUAL_GEMINI_API_KEY or env key and restart."
#         )

#     inp = req.input or {}

#     t0 = time.time()
#     try:
#         j = await _gemini_call_json(inp)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Gemini error: {e}")

#     # For metrics, estimate "num_pages" if PDFs were included and expanded (legacy).
#     # In new SDK we cannot know page count cheaply; report at least 1.
#     num_pages_hint = 1
#     if _client_mode == "google-generativeai":
#         # best-effort: if caller passed a limit, assume up to that
#         num_pages_hint = int(inp.get("pdf_page_limit") or 1)

#     result = _normalize_result(j, num_pages=num_pages_hint)
#     result["latency_ms_total"] = int((time.time() - t0) * 1000)
#     return result
