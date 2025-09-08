#!/usr/bin/env python3
"""
Suresight AI — Governance Agent Tester
- Pings /health
- Builds an OCR payload from:
    a) --ocr-json file, or
    b) --image (calls OCR agent), or
    c) synthetic demo content (default)
- Calls /a2a/govern and prints a concise summary (and detailed dumps with --verbose)

Usage examples:
  python suresight_govern_tester.py --verbose
  python suresight_govern_tester.py --role client --no-gdpr --no-hipaa
  python suresight_govern_tester.py --ocr-json sample_ocr.json --role admin
  python suresight_govern_tester.py --image "C:/path/to/invoice.png" --role client --verbose

Requires:
  pip install httpx python-dotenv
"""

import os, sys, json, time, argparse, base64, mimetypes
from typing import Dict, Any, Tuple

# Load .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

import httpx  # type: ignore


# -------------------- Helpers --------------------
def pretty(x: Any) -> str:
    return json.dumps(x, indent=2, ensure_ascii=False)

def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def b64_from_path(path: str) -> Tuple[str, str]:
    mt, _ = mimetypes.guess_type(path)
    if not mt:
        if path.lower().endswith(".png"): mt = "image/png"
        elif path.lower().endswith((".jpg", ".jpeg")): mt = "image/jpeg"
        else: mt = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8"), mt

def make_synthetic_ocr(confidence: float = 0.92) -> Dict[str, Any]:
    text = (
        "Patient: John Doe\n"
        "DOB: 01/01/1980\n"
        "Email: john.doe@example.com\n"
        "Phone: +1 (415) 555-1212\n"
        "MRN: A12-99-XY\n"
        "Diagnosis: Hypertension\n"
        "Invoice Total: $2,500.00\n"
    )
    return {
        "full_text": text,
        "entities": [
            {"name":"patient_name","value":"John Doe","type":"PII","confidence":0.98},
            {"name":"dob","value":"01/01/1980","type":"DOB","confidence":0.96},
            {"name":"email","value":"john.doe@example.com","type":"EMAIL","confidence":0.97},
            {"name":"phone","value":"+1 (415) 555-1212","type":"PHONE","confidence":0.94},
            {"name":"mrn","value":"A12-99-XY","type":"MRN","confidence":0.93},
            {"name":"diagnosis","value":"Hypertension","type":"medical","confidence":0.91},
            {"name":"invoice_total","value":"$2,500.00","type":"AMOUNT","confidence":0.94}
        ],
        "tables": [
            {"id":"line_items","rows":[
                ["Item","Qty","Price","Contact"],
                ["USB-C Cable","2","$10.00","john.doe@example.com"]
            ]}
        ],
        "doc_class": "clinical_invoice",
        "confidence": float(confidence)
    }

def get_ocr_via_agent(ocr_base: str, image_path: str, timeout: float) -> Dict[str, Any]:
    b64, mt = b64_from_path(image_path)
    payload = {
        "protocol":"a2a.v1",
        "intent":"doc.extract",
        "job_id":f"govtest-ocr-{int(time.time())}",
        "input":{"page_images_b64":[b64], "hints":{"locale":"en-IN"}}
    }
    with httpx.Client(timeout=timeout) as cli:
        r = cli.post(f"{ocr_base}/a2a/ocr", json=payload)
        if r.status_code != 200:
            raise RuntimeError(f"OCR call failed ({r.status_code}): {r.text[:300]}")
        return r.json()


# -------------------- Main --------------------
def main():
    ap = argparse.ArgumentParser(description="Governance Agent Tester")
    ap.add_argument("--host", default=os.getenv("SURE_HOST", "127.0.0.1"))
    ap.add_argument("--gov-port", type=int, default=int(os.getenv("GOV_PORT", "8082")))
    ap.add_argument("--ocr-port", type=int, default=int(os.getenv("OCR_PORT", "8081")))
    ap.add_argument("--role", choices=["admin","client"], default="client")
    ap.add_argument("--gdpr", dest="gdpr", action="store_true", default=True)
    ap.add_argument("--no-gdpr", dest="gdpr", action="store_false")
    ap.add_argument("--hipaa", dest="hipaa", action="store_true", default=True)
    ap.add_argument("--no-hipaa", dest="hipaa", action="store_false")
    ap.add_argument("--confidence", type=float, default=0.92, help="Used only for synthetic OCR")
    ap.add_argument("--ocr-json", help="Path to OCR JSON file (bypass OCR agent)")
    ap.add_argument("--image", help="Path to PNG/JPG; if set, will call OCR agent first")
    ap.add_argument("--timeout", type=float, default=90.0, help="HTTP timeout (seconds)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    gov_base = f"http://{args.host}:{args.gov_port}"
    ocr_base = f"http://{args.host}:{args.ocr_port}"

    # 1) Health check
    try:
        with httpx.Client(timeout=10) as cli:
            r = cli.get(f"{gov_base}/health")
        print(f"[Governance] GET /health -> {r.status_code}")
        if args.verbose:
            try: print(pretty(r.json()))
            except Exception: print(r.text)
        if r.status_code != 200:
            print("[error] governance health failed")
            sys.exit(1)
    except Exception as e:
        print(f"[error] cannot reach governance /health: {e}", file=sys.stderr)
        sys.exit(2)

    # 2) Build OCR payload
    if args.ocr_json:
        try:
            ocr = read_json(args.ocr_json)
            print("[info] Using OCR JSON file")
        except Exception as e:
            print(f"[error] reading --ocr-json: {e}", file=sys.stderr)
            sys.exit(2)
    elif args.image:
        try:
            print("[info] Calling OCR agent with image...")
            ocr = get_ocr_via_agent(ocr_base, args.image, timeout=args.timeout)
        except Exception as e:
            print(f"[error] OCR agent call failed: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        print("[info] Using synthetic OCR content")
