import httpx, base64, os, json

OCR = "http://127.0.0.1:8081"
GOV = "http://127.0.0.1:8082"
REI = "http://127.0.0.1:8083"

with open(r"C:\Users\ParthSurydhwaj\Downloads\OIP.jpg", "rb") as f:
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
print(json.dumps(r.json(), indent=2))
