#!/usr/bin/env python3
"""
Suresight AI - API/Endpoint Probe
Checks health and basic functionality of:
  - OCR service       (/health, /a2a/ocr)
  - Governance service(/health, /a2a/govern)
  - Reinforcement     (/health, /a2a/feedback)

Usage:
  python suresight_api_tester.py [--image path/to.png] [--role admin|client] [--host 127.0.0.1] [--ports 8081 8082 8083]

If --image is omitted, a synthetic test image is generated in-memory.
Exits with code 0 if core checks pass; non-zero otherwise.
"""

import os, sys, io, time, json, base64, argparse
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import httpx
except Exception as e:
    print("Please install httpx: pip install httpx python-dotenv Pillow", file=sys.stderr)
    raise

# Optional: generate a simple image if none provided
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except Exception:
    PIL_OK = False

@dataclass
class ServiceURLs:
    ocr: str
    gov: str
    reinf: str

def b64_from_image_file(path: str) -> Tuple[str, str]:
    import mimetypes
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    mt, _ = mimetypes.guess_type(path)
    if not mt:
        # fallback for common types
        if path.lower().endswith(".png"): mt = "image/png"
        elif path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"): mt = "image/jpeg"
        else: mt = "application/octet-stream"
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8"), mt

def make_synthetic_invoice(size=(900, 600)) -> Tuple[str, str]:
    if not PIL_OK:
        raise RuntimeError("Pillow not installed; cannot synthesize image. Pass --image instead.")
    W, H = size
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    text = (
        "ACME SUPPLIES\n"
        "Invoice #: INV-2025-0912\n"
        "Date: 2025-09-01\n"
        "Bill To: Rahul Sharma\n"
        "Email: rahul.sharma@example.com\n"
        "Line Items:\n"
        "1) USB-C Cable x2  ₹1,000.00\n"
        "2) Laptop Stand x1 ₹3,999.00\n"
        "Subtotal:           ₹4,999.00\n"
        "GST (18%):          ₹899.82\n"
        "TOTAL DUE:          ₹5,898.82\n"
        "Due Date: 2025-09-15\n"
    )
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    y = 40
    for line in text.split("\n"):
        d.text((40, y), line, fill="black", font=font)
        y += 28
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return base64.b64encode(bio.read()).decode("utf-8"), "image/png"

def post_json(url: str, payload: Dict[str, Any], timeout: float=60.0) -> Tuple[int, Dict[str, Any], float]:
    t0 = time.time()
    with httpx.Client(timeout=timeout) as cli:
        r = cli.post(url, json=payload)
        elapsed = (time.time() - t0) * 1000.0
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text}
        return r.status_code, data, elapsed

def get_json(url: str, timeout: float=10.0) -> Tuple[int, Dict[str, Any], float]:
    t0 = time.time()
    with httpx.Client(timeout=timeout) as cli:
        r = cli.get(url)
        elapsed = (time.time() - t0) * 1000.0
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text}
        return r.status_code, data, elapsed

def build_urls(host: str, ocr_port: int, gov_port: int, reinf_port: int) -> ServiceURLs:
    return ServiceURLs(
        ocr=f"http://{host}:{ocr_port}",
        gov=f"http://{host}:{gov_port}",
        reinf=f"http://{host}:{reinf_port}",
    )

def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)

def main():
    ap = argparse.ArgumentParser(description="Probe Suresight AI services")
    ap.add_argument("--host", default=os.getenv("SURE_HOST", "127.0.0.1"))
    ap.add_argument("--ocr-port", type=int, default=int(os.getenv("OCR_PORT", "8081")))
    ap.add_argument("--gov-port", type=int, default=int(os.getenv("GOV_PORT", "8082")))
    ap.add_argument("--reinf-port", type=int, default=int(os.getenv("REINF_PORT", "8083")))
    ap.add_argument("--image", help="PNG/JPG path. If omitted, a synthetic invoice is generated.")
    ap.add_argument("--role", choices=["admin","client"], default="client")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    urls = build_urls(args.host, args.ocr_port, args.gov_port, args.reinf_port)
    failures = 0

    print("=== Health checks ===")
    for name, base in (("OCR", urls.ocr), ("Governance", urls.gov), ("Reinforcement", urls.reinf)):
        code, data, ms = get_json(f"{base}/health")
        ok = (code == 200) and bool(data.get("ok", True))  # reinf stub may not include ok
        print(f"[{name:12}] GET /health -> {code} in {ms:.1f} ms  ok={ok}")
        if args.verbose: print(pretty(data))
        if code != 200:
            failures += 1

    print("\n=== OCR functional test ===")
    if args.image:
        b64, mime = b64_from_image_file(args.image)
    else:
        try:
            b64, mime = make_synthetic_invoice()
            print("[info] Using synthetic invoice image")
        except Exception as e:
            print(f"[warn] Could not synthesize image: {e}. Please pass --image path/to.png", file=sys.stderr)
            sys.exit(2)

    ocr_payload = {
        "protocol":"a2a.v1",
        "intent":"doc.extract",
        "job_id":"probe-ocr-001",
        "input":{"page_images_b64":[b64], "hints":{"locale":"en-IN"}}
    }
    code, ocr, ms = post_json(f"{urls.ocr}/a2a/ocr", ocr_payload, timeout=args.timeout)
    print(f"[OCR         ] POST /a2a/ocr -> {code} in {ms:.1f} ms")
    if args.verbose or code != 200:
        print(pretty(ocr))
    if code != 200:
        failures += 1
    else:
        # Basic sanity
        ft = ocr.get("full_text","")
        ent = ocr.get("entities",[])
        if not ft:
            print("[warn] OCR returned empty full_text")
        if not isinstance(ent, list):
            print("[warn] OCR entities not a list")

    print("\n=== Governance functional test ===")
    gov_payload = {
        "protocol":"a2a.v1",
        "intent":"doc.govern",
        "job_id":"probe-gov-001",
        "input":{
            "ocr_result": ocr if code==200 else {"full_text":"Test text","entities":[],"tables":[]},
            "viewer":{"role": args.role},
            "jurisdiction":{"gdpr": True, "hipaa": True, "region":"EU"},
            "lawful_basis":"contract",
            "retention_days":365
        }
    }
    code2, gov, ms2 = post_json(f"{urls.gov}/a2a/govern", gov_payload, timeout=args.timeout)
    print(f"[Governance  ] POST /a2a/govern -> {code2} in {ms2:.1f} ms")
    if args.verbose or code2 != 200:
        print(pretty(gov))
    if code2 != 200:
        failures += 1
    else:
        sv = (gov.get("views") or {}).get("sanitized", {})
        if "full_text" not in sv:
            print("[warn] Governance sanitized view missing 'full_text'")

    print("\n=== Reinforcement functional test ===")
    feedback_payload = {
        "protocol":"a2a.v1",
        "intent":"feedback.apply",
        "job_id":"probe-reinf-001",
        "input":{
            "original":{"entities":[{"name":"invoice_total","value":"100.00","confidence":0.6}]},
            "corrected":{"entities":[{"name":"invoice_total","value":"120.00","confidence":0.95}]},
            "notes":"probe test"
        }
    }
    code3, reinf, ms3 = post_json(f"{urls.reinf}/a2a/feedback", feedback_payload, timeout=args.timeout)
    print(f"[Reinforcement] POST /a2a/feedback -> {code3} in {ms3:.1f} ms")
    if args.verbose or code3 != 200:
        print(pretty(reinf))
    if code3 != 200:
        failures += 1

    print("\n=== Summary ===")
    print(f"OCR /health:         {'OK' if code==200 else 'FAIL'}")
    print(f"Governance /health:  {'OK' if code2==200 else 'FAIL'}")
    print(f"Reinf /health:       {'OK' if code3==200 else 'FAIL'}")

    if failures:
        print(f"\nResult: FAIL ({failures} issue(s) detected)")
        sys.exit(1)
    else:
        print("\nResult: PASS (all core endpoints responsive)")
        sys.exit(0)

if __name__ == "__main__":
    main()
