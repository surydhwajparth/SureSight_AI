import httpx, base64, os, json

OCR = "https://suresight-ai-ocr.onrender.com/"
GOV = "https://governance-suresight-ai.onrender.com"
REI = "https://reinforce-suresight-ai.onrender.com"

with open(r"demo_data/OIP.jpeg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

# 1) OCR
o = httpx.post(f"{OCR}/a2a/ocr", json={
    "protocol": "a2a.v1",
    "intent": "doc.extract",
    "job_id": "demo-1",
    "input": {"page_images_b64": [b64]}
}, timeout=120.0)
o.raise_for_status()
o_data = o.json()

# 2) Governance (returns full object with views.sanitized inside)
g = httpx.post(f"{GOV}/a2a/govern", json={
    "protocol":"a2a.v1","intent":"doc.govern","job_id":"demo-1",
    "input":{
        "ocr_result": o_data,
        "viewer": {"role": "client"},
        "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
        "lawful_basis": "contract",
        "retention_days": 365
    }
}, timeout=60.0)
g.raise_for_status()
g_data = g.json()

# 3) Reinforcement — pass the FULL governance_result
r = httpx.post(f"{REI}/a2a/reinforce", json={
    "protocol":"a2a.v1","intent":"doc.reinforce","job_id":"demo-1",
    "input":{
        "apply": True,
        "feedback": "Make the date yyyy-mm-dd. Keep the 'Terms of instructions' above other content.",
        "governance_result": g_data,   # <--- FULL governance result here
        "viewer": {"role": "client"},
        "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
        "lawful_basis": "contract",
        "retention_days": 365
    }
}, timeout=90.0)
r.raise_for_status()


print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print()
print(o.status_code, o.text)
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print(g.text)
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
print(r.text)
# print(json.dumps(r.json(), indent=2))

# # test_pipeline.py
# import os, sys, json, base64, argparse, time
# import httpx
# from typing import List

# # -------- Endpoints (env overrides) --------
# OCR = os.getenv("OCR_URL", "http://127.0.0.1:8081")
# GOV = os.getenv("GOV_URL", "http://127.0.0.1:8082")
# REI = os.getenv("REI_URL", "http://127.0.0.1:8083")

# # -------- Timeouts aligned with app.py --------
# HTTPX_HEALTH_TIMEOUT = httpx.Timeout(connect=5, read=5, write=5, pool=5)
# HTTPX_OCR_TIMEOUT    = httpx.Timeout(connect=10, read=180, write=60, pool=10)
# HTTPX_GOV_TIMEOUT    = httpx.Timeout(connect=10, read=90,  write=45, pool=10)
# HTTPX_REI_TIMEOUT    = httpx.Timeout(connect=10, read=90,  write=45, pool=10)

# def b64_from_path(path: str) -> str:
#     with open(path, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")

# def ping_health() -> dict:
#     out = {}
#     try:
#         with httpx.Client(timeout=HTTPX_HEALTH_TIMEOUT) as cli:
#             out["OCR"] = cli.get(f"{OCR}/health").json()
#             out["GOV"] = cli.get(f"{GOV}/health").json()
#             out["REI"] = cli.get(f"{REI}/health").json()
#     except Exception as e:
#         out["__error__"] = str(e)
#     return out

# def call_ocr(img_b64: str, job_id: str, locale: str) -> dict:
#     payload = {
#         "protocol": "a2a.v1",
#         "intent": "doc.extract",
#         "job_id": job_id,
#         "input": {
#             "page_images_b64": [img_b64],
#             "hints": {"locale": locale}
#         }
#     }
#     with httpx.Client(timeout=HTTPX_OCR_TIMEOUT) as cli:
#         resp = cli.post(f"{OCR}/a2a/ocr", json=payload)
#         resp.raise_for_status()
#         data = resp.json()

#     # quick retry if full_text/entities/tables all empty
#     if not (data.get("full_text") or (data.get("entities") or data.get("tables"))):
#         time.sleep(0.4)
#         with httpx.Client(timeout=HTTPX_OCR_TIMEOUT) as cli:
#             resp = cli.post(f"{OCR}/a2a/ocr", json={**payload, "job_id": job_id + "-retry"})
#             resp.raise_for_status()
#             data = resp.json()
#     return data

# def call_governance(ocr_data: dict, job_id: str, role: str = "client") -> dict:
#     payload = {
#         "protocol": "a2a.v1",
#         "intent": "doc.govern",
#         "job_id": job_id,
#         "input": {
#             "ocr_result": ocr_data,
#             "viewer": {"role": role},
#             "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#             "lawful_basis": "contract",
#             "retention_days": 365
#         }
#     }
#     with httpx.Client(timeout=HTTPX_GOV_TIMEOUT) as cli:
#         resp = cli.post(f"{GOV}/a2a/govern", json=payload)
#         resp.raise_for_status()
#         return resp.json()

# def call_reinforce(gov_data: dict, job_id: str, role: str, feedback: str, apply_flag: bool = True) -> dict:
#     payload = {
#         "protocol": "a2a.v1",
#         "intent": "doc.reinforce",
#         "job_id": job_id,
#         "input": {
#             "apply": bool(apply_flag),
#             "feedback": feedback or "",
#             "governance_result": gov_data,  # pass the FULL governance object
#             "viewer": {"role": role},
#             "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#             "lawful_basis": "contract",
#             "retention_days": 365
#         }
#     }
#     with httpx.Client(timeout=HTTPX_REI_TIMEOUT) as cli:
#         resp = cli.post(f"{REI}/a2a/reinforce", json=payload)
#         resp.raise_for_status()
#         return resp.json()

# def summarize_ocr(ocr: dict) -> str:
#     words = len((ocr.get("full_text") or "").split())
#     ents  = len(ocr.get("entities") or [])
#     tabs  = len(ocr.get("tables") or [])
#     conf  = float(ocr.get("confidence") or 0.0)
#     cls   = ocr.get("doc_class", "unknown")
#     return f"class={cls} | conf={conf:.2f} | words={words} | entities={ents} | tables={tabs}"

# def main(paths: List[str], role: str, locale: str, feedback: str, apply_flag: bool):
#     print("=== Health ===")
#     print(json.dumps(ping_health(), indent=2))
#     print()

#     for i, p in enumerate(paths, start=1):
#         job_id = f"demo-{int(time.time())}-{i}"
#         print(f"--- File {i}/{len(paths)}: {p} ---")

#         try:
#             b64 = b64_from_path(p)
#         except Exception as e:
#             print(f"[x] Read failed: {e}")
#             continue

#         # 1) OCR
#         try:
#             ocr = call_ocr(b64, job_id + "-ocr", locale)
#             print("[OCR]  ", summarize_ocr(ocr))
#         except Exception as e:
#             print(f"[x] OCR error: {e}")
#             continue

#         # 2) Governance
#         try:
#             gov = call_governance(ocr, job_id + "-gov", role=role)
#             sanitized = (gov.get("views") or {}).get("sanitized") or {}
#             redactions = len(gov.get("redaction_manifest") or [])
#             policy = gov.get("policy_version")
#             print(f"[GOV]  policy={policy} | redactions={redactions}")
#         except Exception as e:
#             print(f"[x] Governance error: {e}")
#             continue

#         # 3) Reinforcement
#         try:
#             rei = call_reinforce(gov, job_id + "-rei", role=role, feedback=feedback, apply_flag=apply_flag)
#             status = rei.get("status")
#             applied = bool((rei.get("audit") or {}).get("applied_feedback"))
#             latency = (rei.get("audit") or {}).get("latency_ms_total")
#             print(f"[REINF] status={status} | applied={applied} | latency_ms={latency}")
#             # Uncomment to inspect the final:
#             # print(json.dumps(rei.get("final"), indent=2, ensure_ascii=False))
#         except Exception as e:
#             print(f"[x] Reinforcement error: {e}")

#         print()

# if __name__ == "__main__":
#     ap = argparse.ArgumentParser(description="SureSight-AI local pipeline tester")
#     ap.add_argument("paths", nargs="+", help="Path(s) to PNG/JPG images")
#     ap.add_argument("--role", default="client", choices=["client","admin"], help="Viewer role")
#     ap.add_argument("--locale", default="en-IN", help="OCR locale hint")
#     ap.add_argument("--feedback", default="Normalize dates to YYYY-MM-DD and keep 'Terms of instructions' above other content.")
#     ap.add_argument("--no-apply", action="store_true", help="Skip applying reinforcement (send apply=false)")
#     args = ap.parse_args()

#     main(args.paths, role=args.role, locale=args.locale, feedback=args.feedback, apply_flag=not args.no_apply)
