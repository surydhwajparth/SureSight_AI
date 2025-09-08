# ocr_smoke_test.py
import os, sys, base64, argparse, mimetypes, json

# Try new SDK first
SDK = None
try:
    from google import genai as genai_new  # pip install google-genai
    SDK = "google-genai"
except Exception:
    try:
        import google.generativeai as genai_old  # pip install google-generativeai
        SDK = "google-generativeai"
    except Exception:
        SDK = None

def read_file_b64(path: str):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode("utf-8"), data

def guess_mime(path: str):
    mt, _ = mimetypes.guess_type(path)
    # sensible fallback for images
    if mt is None:
        if path.lower().endswith(".png"): return "image/png"
        if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"): return "image/jpeg"
    return mt or "image/png"

def genai_transcribe_image_google_genai(api_key: str, model_name: str, img_path: str) -> str:
    from google import genai as genai
    client = genai.Client(api_key=api_key)
    b64, _ = read_file_b64(img_path)
    mime = guess_mime(img_path)
    # Ask for plain text transcription (OCR)
    resp = client.models.generate_content(
        model=model_name,
        contents=[{
            "role": "user",
            "parts": [
                {"text": "Transcribe all visible text from this image. Respond with PLAIN TEXT only—no JSON, no markdown."},
                {"inline_data": {"mime_type": mime, "data": b64}}
            ],
        }],
        generation_config={"temperature": 0.0, "max_output_tokens": 4096}
    )
    text = getattr(resp, "output_text", None) or getattr(resp, "text", None)
    if not text:
        # lenient fallback: try to dig into candidates
        try:
            cand = resp.candidates[0]
            for p in cand.content.parts:
                if hasattr(p, "text") and p.text:
                    text = p.text
                    break
        except Exception:
            text = ""
    return text or ""

def genai_transcribe_image_legacy(api_key: str, model_name: str, img_path: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    b64, _ = read_file_b64(img_path)
    mime = guess_mime(img_path)
    resp = model.generate_content(
        contents=[{
            "role": "user",
            "parts": [
                {"text": "Transcribe all visible text from this image. Respond with PLAIN TEXT only—no JSON, no markdown."},
                {"inline_data": {"mime_type": mime, "data": b64}}
            ],
        }],
        generation_config={"temperature": 0.0, "max_output_tokens": 4096}
    )
    text = getattr(resp, "text", None)
    if not text:
        try:
            cand = resp.candidates[0]
            for p in cand.content.parts:
                if hasattr(p, "text") and p.text:
                    text = p.text
                    break
        except Exception:
            text = ""
    return text or ""

def main():
    p = argparse.ArgumentParser(description="Gemini OCR Smoke Test (no agents)")
    p.add_argument("image", help="Path to PNG/JPG to OCR")
    p.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                   help="Model name (default: gemini-2.5-flash)")
    p.add_argument("--key", default=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
                   help="API key (or set GEMINI_API_KEY / GOOGLE_API_KEY env vars)")
    args = p.parse_args()

    if not SDK:
        print("ERROR: No Gemini SDK installed. Run one of:\n"
              "  pip install google-genai\n"
              "  # or\n"
              "  pip install google-generativeai", file=sys.stderr)
        sys.exit(2)

    if not args.key:
        print("ERROR: No API key. Pass --key or set GEMINI_API_KEY / GOOGLE_API_KEY.", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(args.image):
        print(f"ERROR: File not found: {args.image}", file=sys.stderr)
        sys.exit(2)

    print(f"[info] SDK: {SDK} | model: {args.model}")
    try:
        if SDK == "google-genai":
            text = genai_transcribe_image_google_genai(args.key, args.model, args.image)
        else:
            text = genai_transcribe_image_legacy(args.key, args.model, args.image)
    except Exception as e:
        print(f"ERROR calling Gemini: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n===== OCR RESULT (plain text) =====\n")
    print(text.strip() or "(empty)")
    print("\n===================================\n")

if __name__ == "__main__":
    main()
