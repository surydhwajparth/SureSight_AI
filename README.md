# SureSight AI – Agentic OCR System

**SureSight AI** is a multi-agent document intelligence system. It combines OCR, governance (privacy redaction), and reinforcement (human-in-the-loop corrections) into a workflow with a Streamlit-based UI.

## 🧩 Components

### 1. OCR Agent (`app/services/ocr_agent.py`)
- Uses **Google Gemini (2.5 Flash)** via `google-genai` or legacy `google-generativeai`.
- Accepts:
  - Base64-encoded images (`page_images_b64`)
  - Remote URLs (`pages`)
  - PDF uploads (`pdf_b64` or `pdf_url`)
- Extracts:
  - `full_text`
  - `entities` (`name`, `value`, `type`, `confidence`)
  - `tables`
  - `doc_class`
  - `confidence`
- Supports retries, MIME sniffing, and JSON-cleanup from model output.
- Health check at `/health`.

### 2. Governance Agent
- Applies compliance rules (GDPR/HIPAA).
- Produces:
  - Sanitized views
  - Redaction manifests
  - Audit trails

### 3. Reinforcement Agent
- Accepts human feedback.
- Uses Gemini to apply transformations (normalize dates, fix tables, etc).
- Produces a new `final` view and audit trail.

### 4. Streamlit UI (`ui/app.py`)
- Upload images or PDFs.
- See OCR → Governance → Reinforcement results step-by-step.
- Interactive tabs:
  - Final View
  - Entities
  - Tables
  - Raw OCR (admin only)
  - Reinforcement
  - Audit Trail
- Sidebar shows live health of agents.
- Dark theme, professional UI.

### 5. OCR Test Script (`ocr_pdf_test_script.py`)
- CLI script to test OCR agent with any local PDF or image.
- Converts file → base64 → sends request.
- Saves results to JSON.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.12+
- `pip install -r requirements.txt`
- A valid **Google Gemini API key**

### Run Agents Locally
Each agent is a FastAPI service:

```bash
# OCR Agent (supports images + PDFs)
uvicorn app.services.ocr_agent:app --host 0.0.0.0 --port 8081 --reload

# Governance Agent
uvicorn app.services.governance_agent:app --host 0.0.0.0 --port 8082 --reload

# Reinforcement Agent
uvicorn app.services.reinforcement_agent:app --host 0.0.0.0 --port 8083 --reload
```

### Run UI Locally
```bash
cd ui
streamlit run app.py
```

The UI will connect to the 3 services at the ports defined in your `.env`:

```env
OCR_PORT=http://localhost:8081
GOV_PORT=http://localhost:8082
REINF_PORT=http://localhost:8083
```

---

## 🌐 Deployment

### Render (Agents)
- Push repo to GitHub.
- Create 3 **Web Services** on Render:
  - OCR → start command: `uvicorn app.services.ocr_agent:app --host 0.0.0.0 --port $PORT`
  - Governance → `uvicorn app.services.governance_agent:app --host 0.0.0.0 --port $PORT`
  - Reinforcement → `uvicorn app.services.reinforcement_agent:app --host 0.0.0.0 --port $PORT`
- Set environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`).

### Streamlit Cloud (UI)
- Create `streamlit_app.py` (or point to `ui/app.py`).
- Add `requirements.txt`.
- Configure `.streamlit/secrets.toml` if needed.
- Deploy on [share.streamlit.io](https://share.streamlit.io).

---

## 🧪 Testing

Run the CLI tester on a PDF:

```bash
python ocr_pdf_test_script.py
```

It will:
1. Hit `/health`
2. Upload the file
3. Print preview of extracted text/entities/tables
4. Save JSON to disk

---

## 📂 Project Structure

```
app/
  services/
    ocr_agent.py           # OCR agent (images + PDFs)
    governance_agent.py    # Privacy / compliance
    reinforcement_agent.py # Human feedback
ui/
  app.py                   # Streamlit frontend
  artifacts/logos/         # Logos
ocr_pdf_test_script.py     # Local test script
requirements.txt
```

---

## ⚖️ License
MIT License – see [LICENSE](LICENSE).
