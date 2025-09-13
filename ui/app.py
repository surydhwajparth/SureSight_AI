# app.py
import os, json, base64, httpx, time, mimetypes

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


load_dotenv()

# ===================== Service endpoints =====================
OCR_URL   = os.getenv("OCR_PORT") or "http://localhost:8081"
GOV_URL   = os.getenv("GOV_PORT") or "http://localhost:8082"
REINF_URL = os.getenv("REINF_PORT") or "http://localhost:8083"

# ===================== Assets =====================
LEFT_LOGO  = r"ui/artifacts/logos/AdrosonicLogo.png"
RIGHT_LOGO = r"ui/artifacts/logos/DILLogo.png"
ECL_Logo = r"ui/artifacts/logos/ECL.png"

# ===================== Defaults (no UI controls) =====================
LOCALE_DEFAULT = "en-IN"
HUMAN_TASK     = "extract"

# ===================== HTTPX timeouts =====================
HTTPX_HEALTH_TIMEOUT = httpx.Timeout(connect=5, read=5, write=5, pool=5)
HTTPX_OCR_TIMEOUT    = httpx.Timeout(connect=10, read=180, write=60, pool=10)
HTTPX_GOV_TIMEOUT    = httpx.Timeout(connect=10, read=90, write=45, pool=10)
HTTPX_REINF_TIMEOUT  = httpx.Timeout(connect=10, read=90, write=45, pool=10)

# ===================== Page config =====================
st.set_page_config(page_title="SureSight AI • Agentic OCR", layout="wide", initial_sidebar_state="expanded")

# ===================== Theme / CSS =====================
STYLES = """
<style>
:root{
  --bg:#0a0f1e; --panel:#0e1430; --glass:rgba(255,255,255,0.06);
  --edge:rgba(255,255,255,0.12); --text:#e6e9f5; --muted:#b6bfdc; --accent:#7dd3fc;
  --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --chip:#11183b; --chipb:#1c2553;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 20% 0%, #0f1a3c 0%, #0a0f1e 45%, #070b18 100%) !important;
}
section[data-testid="stSidebar"] {
  background: #0b122e !important; border-right: 1px solid var(--edge);
}
section[data-testid="stSidebar"] .block-container { padding-top:.6rem; }
.block-container {padding-top: .8rem; padding-bottom: 2rem; max-width: 1800px;}
* { color: var(--text); }
a { color: var(--accent); }

/* Sidebar logos */
.sidebar-logos { display:flex; gap:12px; align-items:center; justify-content:center; margin:6px 6px 14px 6px; }
.sidebar-logos img { height:34px; border-radius:8px; padding:6px 8px; border:1px solid var(--edge); }

/* Cards */
.su-surface { background: linear-gradient(160deg, var(--panel) 0%, #0c1233 100%);
              border: 1px solid var(--edge); border-radius: 18px; padding: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset;}
.su-glass { background: var(--glass); border: 1px solid var(--edge); border-radius: 18px; padding: 18px; backdrop-filter: blur(10px); }
.su-card  { background: #0e1534; border:1px solid var(--edge); border-radius:16px; padding:16px; }

/* Chips / dots */
.su-chip { display:inline-flex; align-items:center; gap:.5rem; padding:6px 12px; border-radius:999px; background:linear-gradient(160deg,var(--chip),var(--chipb)); border:1px solid var(--edge); font-size:.85rem; }
.su-dot {width:10px; height:10px; border-radius:50%;}
.ok {background: var(--ok);} .warn{background:var(--warn);} .bad{background:var(--bad);}

/* HERO header (centered banner) */
.su-hero { border-radius: 22px; padding: 28px; margin-bottom: 16px;
           background: linear-gradient(135deg, #1f3b8a 20%, #0ea5e9 40%, #2563eb 100%);
           box-shadow: 0 20px 80px rgba(14,165,233,.25); text-align:center; }
.su-hero h1 { margin:0; font-weight:900; letter-spacing:.4px; font-size:2.2rem; color:#e6f1ff; }
.su-hero p  { margin:.35rem 0 0 0; color:#d9ecff; opacity:.95; font-weight:600; }

/* Metrics */
.stat {text-align:center; background: var(--glass); border:1px solid var(--edge); border-radius:14px; padding:10px;}
.metric {font-size:1.15rem; font-weight:800;}

/* Sidebar agent cards */
.sidebar-title {font-weight:700; margin-bottom:.2rem;}
.agent-card {border:1px solid var(--edge); border-radius:14px; padding:12px; margin-bottom:12px; background:var(--glass);}
.agent-row {display:flex; align-items:center; justify-content:space-between;}
.agent-name {font-weight:600;}
.agent-step {color:var(--muted); font-size:.85rem;}
.progress-wrap {height:6px; background:#10193b; border-radius:999px; overflow:hidden; margin-top:8px;}
.progress-inner {height:100%; background:linear-gradient(90deg,#22d3ee,#60a5fa,#a78bfa); width:0%;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {padding: 10px 18px; border-radius: 10px 10px 0 0; background: #0e1534; border: 1px solid var(--edge);}
.stTabs [aria-selected="true"] {background: linear-gradient(160deg,#1e293b,#0b122e); color: white; border-bottom-color: transparent;}

/* Inputs / Selects: keep select white text-on-dark dropdown content readable */
div[data-baseweb="select"] > div { background:#0e1534 !important; border:1px solid var(--edge) !important; }
div[data-baseweb="select"] * { color:#e6e9f5 !important; }
ul[role="listbox"] li { color:#000 !important; }

/* FILE UPLOADER: dark container + dark "Browse files" button */
div[data-testid="stFileUploadDropzone"] {
  background: var(--glass) !important;
  border:1px solid var(--edge) !important;
  color: var(--text) !important;
}
div[data-testid="stFileUploadDropzone"] button {
  color: var(--text) !important;
  background:#172043 !important;
  border:1px solid var(--edge) !important;
}
div[data-testid="stFileUploadDropzone"] button:hover { background:#1c2553 !important; }

/* Buttons (includes sidebar Refresh health, Apply Feedback, Download Final Text) */
.stButton>button, .stDownloadButton>button {
  border-radius:12px;
  background: linear-gradient(160deg,#0b122e,#0f1844) !important;
  color: var(--text) !important;
  border:1px solid var(--edge) !important;
}
.stButton>button:disabled, .stDownloadButton>button:disabled {
  background:#1b244b !important; color:#94a3b8 !important; border-color:#2a355f !important;
}

/* Expander headers (Tables) */
div[data-testid="stExpander"] {
  border:1px solid var(--edge); border-radius:12px; background:var(--glass);
}
div[data-testid="stExpander"] > details > summary {
  background:#0e1534; color:var(--text); padding:10px 12px; border-bottom:1px solid var(--edge);
}

/* Alerts & info boxes */
div[role="alert"] {
  background: var(--glass) !important;
  border:1px solid var(--edge) !important;
  color: var(--text) !important;
}



/* Sanitized text pane */
.sanitized-shell { border-radius:16px; overflow:hidden; border:1px solid var(--edge); }
.sanitized-bar { display:flex; gap:10px; align-items:center; padding:10px 12px; background:linear-gradient(160deg,#0b122e,#0f1844); border-bottom:1px solid var(--edge); }
.sanitized-body { background: #0a0f1e; padding:14px; max-height:420px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; line-height:1.55; }
.redacted { background: rgba(239,68,68,.15); border: 1px dashed rgba(239,68,68,.5); padding: 2px 6px; border-radius:6px; color:#fecaca; }

footer {visibility:hidden;}
.stSpinner > div > div {border-color: #38bdf8 transparent transparent transparent;}
</style>
"""

st.markdown(STYLES, unsafe_allow_html=True)

# ===================== App State =====================
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "OCR": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting"},
        "Gov": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting"},
        "Reinf": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting"},
    }
if "results" not in st.session_state:
    st.session_state.results = []   # list of dicts, one per image
if "role" not in st.session_state:
    st.session_state.role = "client"

# ===================== Helpers =====================
def set_agent(key, status=None, pct=None, tone=None, step=None):
    cur = st.session_state.agent_state.get(key, {})
    if status is not None: cur["status"]=status
    if pct is not None: cur["pct"]=pct
    if tone is not None: cur["tone"]=tone
    if step is not None: cur["step"]=step
    st.session_state.agent_state[key]=cur
def agent_panel():
    c_logo1, c_logo2 = st.sidebar.columns([1,1])
    try:
        c_logo1.image(LEFT_LOGO)
    except Exception:
        c_logo1.markdown("🔍")
    try:
        c_logo2.image(RIGHT_LOGO)
    except Exception:
        c_logo2.markdown("🛡️")

    # Set sidebar transparency to 120% (opacity > 1 is not valid, so use 1 for max opacity)
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: rgba(11, 18, 46, 0.20) !important; /* 100% opacity */
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### ⚙️ Agents")
    st.sidebar.caption("Live status while your document(s) are processed.")
    for label, key, icon in [("OCR Engine","OCR","🔤"), ("Governance","Gov","🛡️"), ("Reinforcement","Reinf","🚀")]:
        s = st.session_state.agent_state.get(key, {})
        st.sidebar.markdown(f"""
        <div class="agent-card">
            <div class="agent-row">
            <div class="agent-name">{icon} {label}</div>
            <div class="su-chip"><span class="su-dot {'ok' if s.get('tone')=='ok' else 'warn' if s.get('tone')=='warn' else 'bad'}"></span>{s.get('status','')}</div>
            </div>
            <div class="agent-step">{s.get('step','')}</div>
            <div class="progress-wrap"><div class="progress-inner" style="width:{int(s.get('pct',0))}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("### 🌐 Services")
    if st.sidebar.button("Refresh health", width='stretch'):
        st.session_state._health = ping_health()
    if "_health" not in st.session_state:
        st.session_state._health = ping_health()
    cols = st.sidebar.columns(3)
    for i,(label,key) in enumerate([("OCR","OCR"),("Gov","Gov"),("Reinf","Reinf")]):
        ok = bool(st.session_state._health.get(key,{}).get("ok", False))
        tone = "ok" if ok else "bad"
        cols[i].markdown(f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}</span>', unsafe_allow_html=True)

def hero_header():
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {background: rgba(0,0,0,0.15) !important;}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:flex; justify-content:center; align-items:center;">'
        f'<img src="data:image/png;base64,{base64.b64encode(open(ECL_Logo, "rb").read()).decode()}" '
        f'style="height:120px; margin-bottom:56px; margin-top:-144px" />'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <div class="su-hero">
      <div style="
        background: linear-gradient(135deg, #0a0f1c 15%, #1e293b 30%, #0f172a 90%);
        border-radius: 24px;
        padding: 32px 48px;
        margin-bottom: 22px;
        box-shadow: 0 8px 48px rgba(150,165,233,0.22);
        text-align: center;
        display: inline-block;
        min-width: 420px;
      ">
        <span style="font-size:2.2rem; font-weight:900; color:#e6f1ff; letter-spacing:.5px;">
            SureSight AI
        </span>
      </div>
      <p style="color:#d9ecff; font-weight:800; margin-top:12px;">
        Agentic OCR • A2A • Gemini 2.5 Flash • HIPAA/GDPR Compliant
      </p>
    </div>
    """, unsafe_allow_html=True)

def metrics_from_current(ocr: dict, final_view: dict):
    words = len((final_view.get("full_text") or "").split())
    ents  = len(final_view.get("entities") or [])
    tabs  = len(final_view.get("tables") or [])
    conf  = float(ocr.get("confidence") or 0.0)
    cls   = ocr.get("doc_class","unknown")
    return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

def fmt_sanitized_html(text, redaction_count, policy_version, role):
    if not text: text = "No text content available."
    safe_html = (text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                    .replace("[REDACTED]", '<span class="redacted">[REDACTED]</span>'))
    toolbar = f"""
    <div class="sanitized-bar">
      <span class="su-chip"><span class="su-dot ok"></span> Sanitized View</span>
      <span class="su-chip">Role: <strong>{role}</strong></span>
      <span class="su-chip">Policy: {policy_version}</span>
      <span class="su-chip">Redactions: <strong>{redaction_count}</strong></span>
    </div>"""
    return f'<div class="sanitized-shell">{toolbar}<div class="sanitized-body">{safe_html}</div></div>'

def b64_for_uploaded(file) -> str:
    try:
        data = file.getvalue()
    except Exception:
        file.seek(0); data = file.read()
    if not data: raise ValueError("Empty upload buffer")
    return base64.b64encode(data).decode("utf-8")

def ping_health():
    try:
        with httpx.Client(timeout=HTTPX_HEALTH_TIMEOUT) as cli:
            return {
                "OCR": cli.get(f"{OCR_URL}/health").json(),
                "Gov": cli.get(f"{GOV_URL}/health").json(),
                "Reinf": cli.get(f"{REINF_URL}/health").json(),
            }
    except Exception:
        return {}

# ---- service wrappers ----
def _call_ocr(img_b64: str, job_id: str, locale: str) -> dict:
    payload = {
        "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
        "input":{"page_images_b64":[img_b64], "hints":{"locale": locale}}
    }
    with httpx.Client(timeout=HTTPX_OCR_TIMEOUT) as cli:
        return cli.post(f"{OCR_URL}/a2a/ocr", json=payload).json()

def _call_governance(ocr: dict, job_id: str, role: str) -> dict:
    payload = {
        "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
        "input":{
            "ocr_result": ocr,
            "viewer": {"role": role},
            "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
            "lawful_basis": "contract",
            "retention_days": 365
        }
    }
    with httpx.Client(timeout=HTTPX_GOV_TIMEOUT) as cli:
        return cli.post(f"{GOV_URL}/a2a/govern", json=payload).json()

def _call_reinforce(gov: dict, job_id: str, role: str, apply: bool, feedback: str) -> dict:
    payload = {
        "protocol":"a2a.v1","intent":"doc.reinforce","job_id":job_id,
        "input":{
            "apply": bool(apply),
            "feedback": feedback or "",
            "governance_result": gov,
            "viewer": {"role": role},
            "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
            "lawful_basis": "contract",
            "retention_days": 365
        }
    }
    with httpx.Client(timeout=HTTPX_REINF_TIMEOUT) as cli:
        return cli.post(f"{REINF_URL}/a2a/reinforce", json=payload).json()

# ===================== UI =====================
def render_app():
    hero_header()
    agent_panel()

    st.markdown("### Workspace")
    with st.container():
        c1, c2 = st.columns([0.65, 0.35])
        with c1:
            uploaded_files = st.file_uploader(
                "📤 Upload Document(s) (PNG / JPG)",
                type=["png","jpg","jpeg"],
                accept_multiple_files=True,
                help="Upload 1–10 images; each will be processed independently.",
            )
        with c2:
            role = st.selectbox("User Role", ["admin","client"], index=1,
                                help="Admin: raw OCR; Client: sanitized")
    st.session_state.role = role

    num_files = len(uploaded_files) if uploaded_files else 0

    run_col, info_col = st.columns([0.25, 0.75])
    with run_col:
        run = st.button("Run Pipeline", type="primary", width='stretch')
    with info_col:
        if num_files > 0:
            st.markdown(
                '<div class="su-chip"><span class="su-dot ok"></span>'
                f'Ready to process: <strong>{num_files}</strong> image(s)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="su-chip"><span class="su-dot warn"></span>'
                'Upload one or more PNG/JPG images to begin processing</div>',
                unsafe_allow_html=True
            )

    # ========== Run Pipeline ==========
    if run:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one PNG/JPG image.")
            st.stop()

        st.session_state.results = []
        n = len(uploaded_files)
        job_base = f"job-{int(time.time())}"

        for k in ["OCR","Gov","Reinf"]:
            set_agent(k, status="Queued", pct=0, tone="warn", step=f"Queued for {n} image(s)")

        progress_bar = st.progress(12)
        status_text = st.empty()

        for i, file in enumerate(uploaded_files, start=1):
            file_name = getattr(file, "name", f"image-{i}.png")

            # ---- OCR ----
            set_agent("OCR", status="Running", pct=int((i-1)/n*25)+5, tone="warn", step=f"OCR {i}/{n}: {file_name}")
            with st.spinner():
                status_text.text(f"🔤 OCR {i}/{n}: {file_name}")
                progress_bar.progress(int((i-1)/n*25)+5)
                try:
                    img_b64 = b64_for_uploaded(file)
                    ocr = _call_ocr(img_b64, f"{job_base}-ocr-{i}", LOCALE_DEFAULT)

                    if not (ocr.get("full_text") or (ocr.get("entities") or ocr.get("tables"))):
                        time.sleep(0.4)
                        ocr = _call_ocr(img_b64, f"{job_base}-ocr-{i}-retry", LOCALE_DEFAULT)
                        if not (ocr.get("full_text") or (ocr.get("entities") or ocr.get("tables"))):
                            raise RuntimeError("OCR returned empty content twice")
                except httpx.TimeoutException:
                    set_agent("OCR", status="Error", pct=int(i/n*25), tone="bad", step=f"Timeout {i}/{n}")
                    st.error(f"OCR timed out for {file_name}")
                    continue
                except Exception as e:
                    set_agent("OCR", status="Error", pct=int(i/n*25), tone="bad", step=f"Failed {i}/{n}")
                    st.error(f"OCR failed for {file_name}: {e}")
                    continue
                set_agent("OCR", status="Complete", pct=int(i/n*25), tone="ok", step=f"OCR done {i}/{n}")

            # ---- Governance ----
                set_agent("Gov", status="Running", pct=25+int((i-1)/n*45)+5, tone="warn", step=f"Governance {i}/{n}")

                progress_bar.progress(min(25+int((i-1)/n*45), 70))
                try:
                    gov = _call_governance(ocr, f"{job_base}-gov-{i}", role)
                except httpx.TimeoutException:
                    set_agent("Gov", status="Error", pct=25+int(i/n*45), tone="bad", step=f"Timeout {i}/{n}")
                    st.error(f"Governance timed out for {file_name}")
                    continue
                except Exception as e:
                    set_agent("Gov", status="Error", pct=25+int(i/n*45), tone="bad", step=f"Failed {i}/{n}")
                    st.error(f"Governance failed for {file_name}: {e}")
                    continue
                set_agent("Gov", status="Complete", pct=25+int(i/n*45), tone="ok", step=f"Sanitized {i}/{n}")

                sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
                redacts   = gov.get("redaction_manifest", []) or []
                gov_audit = gov.get("audit", {}) or {}

                st.session_state.results.append({
                    "file_name": file_name, "ocr": ocr, "gov": gov,
                    "sanitized": sanitized, "final": sanitized,
                    "redacts": redacts, "gov_audit": gov_audit, "reinf": None
                })

                progress_bar.progress(min(25+int(i/n*65), 70))

            set_agent("Reinf", status="Idle", pct=80, tone="warn", step="Awaiting feedback per image")
            progress_bar.progress(100)
        status_text.text("✅ OCR & Governance complete. Use the Reinforcement tabs below if needed.")
        time.sleep(0.4)
        progress_bar.empty(); status_text.empty()

    # ========== Results ==========
    if st.session_state.results:
        st.markdown("### 📊 Document Analysis (per image)")
        for idx, res in enumerate(st.session_state.results, start=1):
            final_view = res["final"]
            ocr = res["ocr"]
            gov = res["gov"]
            redacts = res["redacts"]
            gov_audit = res["gov_audit"]
            role = st.session_state.role

            # Metrics row (from FINAL view)
            m = metrics_from_current(ocr, final_view)
            st.markdown(f"#### 📄 {idx}. {res['file_name']}")
            c1,c2,c3,c4,c5 = st.columns(5)
            with c1:
                st.markdown(f'<div class="su-glass stat">📄<div>Document Type</div><div class="metric">{m["doc_class"]}</div></div>', unsafe_allow_html=True)
            with c2:
                color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
                st.markdown(f'<div class="su-glass stat">{color}<div>Confidence</div><div class="metric">{m["confidence"]:.2f}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="su-glass stat">📝<div>Words</div><div class="metric">{m["words"]:,}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="su-glass stat">🏷️<div>Entities</div><div class="metric">{m["entities"]}</div></div>', unsafe_allow_html=True)
            with c5:
                st.markdown(f'<div class="su-glass stat">📊<div>Tables</div><div class="metric">{m["tables"]}</div></div>', unsafe_allow_html=True)

            # Tabs
            if role == "admin":
                tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🔍 Raw OCR", "🚀 Reinforcement", "📋 Audit"]
                idx_raw, idx_reinf, idx_audit = 3, 4, 5
            else:
                tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🚀 Reinforcement", "📋 Audit"]
                idx_reinf, idx_audit = 3, 4
            tabs = st.tabs(tab_labels)

            # Final View
            with tabs[0]:
                st.markdown("##### 🔒 Final View")
                html = fmt_sanitized_html(final_view.get("full_text",""), len(redacts), gov.get("policy_version","N/A"), role)
                st.markdown(html, unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download Final Text",
                    data=(final_view.get("full_text") or "").encode("utf-8"),
                    file_name=f"{res['file_name']}-final.txt",
                    mime="text/plain",
                    width='stretch'
                )

            # Entities
            with tabs[1]:
                st.markdown("##### 🏷️ Entities (Final)")
                ents = final_view.get("entities", []) or []
                if ents:
                    df = pd.DataFrame(ents)
                    if 'redacted' in df.columns:
                        df['visibility'] = df['redacted'].map({True:'🔒 Protected', False:'👁️ Visible'})
                    st.dataframe(df, width='stretch', height=320)
                else:
                    st.info("🔍 No entities detected.")

            # Tables
            with tabs[2]:
                st.markdown("##### 📊 Document Tables (Final)")
                tables = final_view.get("tables", []) or []
                if tables:
                    for i,t in enumerate(tables):
                        with st.expander(f"📋 Table {i+1}: {t.get('id','Unnamed')}", expanded=(i==0)):
                            rows = t.get("rows", []) or []
                            if rows:
                                try:
                                    header, *data = rows if len(rows) > 1 else ([], rows)
                                    if header and data and all(len(r) == len(header) for r in data):
                                        df = pd.DataFrame(data, columns=header)
                                    else:
                                        df = pd.DataFrame(rows)
                                    st.dataframe(df, width='stretch', height=240)
                                except Exception:
                                    st.dataframe(pd.DataFrame(rows), width='stretch', height=240)
                            else:
                                st.info("📝 Empty table.")
                else:
                    st.info("📊 No tables detected.")

            # Raw OCR (Admin)
            if role == "admin" and len(tabs) > 3:
                with tabs[idx_raw]:
                    st.markdown("##### 🔍 Raw OCR Output")
                    st.json(ocr)

            # Reinforcement (NO audit/JSON here)
            with tabs[idx_reinf]:
                st.markdown("##### 🚀 Reinforcement: Human Feedback")
                with st.form(f"reinforcement_form_{idx}", clear_on_submit=False):
                    apply_flag = st.checkbox("Apply reinforcement", value=True, help="Use Gemini to apply your feedback safely.")
                    feedback_text = st.text_area(
                        "📝 Your Feedback",
                        height=120,
                        placeholder="e.g., Standardize dates to YYYY-MM-DD, normalize currency, fix mislabeled columns.",
                        key=f"fb_{idx}"
                    )
                    submitted = st.form_submit_button("Apply Feedback", width='stretch', type="primary" )

                if submitted:
                    set_agent("Reinf", status="Running", pct=85, tone="warn",
                              step=f"Optimizing {idx}/{len(st.session_state.results)}")
                    try:
                        reinf = _call_reinforce(res["gov"], f"reinf-{int(time.time())}-{idx}", role, apply_flag, feedback_text)
                        res["reinf"] = reinf
                        if reinf.get("status") == "ok":
                            res["final"] = reinf.get("final") or res["sanitized"]   # update main view
                            set_agent("Reinf", status="Complete", pct=100, tone="ok", step="Finalized")
                            st.success("Reinforcement applied. The Final View, Entities and Tables above have been updated.")
                            st.rerun()
                        elif reinf.get("status") == "skipped":
                            set_agent("Reinf", status="Skipped", pct=90, tone="warn", step="Skipped by user")
                            st.info("Reinforcement skipped. Showing sanitized output.")
                        else:
                            set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent error")
                            st.error(reinf.get("detail") or "Reinforcement error.")
                    except Exception as e:
                        set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent call failed")
                        st.exception(e)

            # Audit tab (governance & reinforcement audit only here)
            with tabs[idx_audit]:
                st.markdown("##### 📋 Compliance Audit Trail")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🕒 Governance Audit**")
                    if gov_audit:
                        st.json({
                            "timestamp": gov_audit.get("timestamp"),
                            "viewer_role": gov_audit.get("viewer_role"),
                            "jurisdiction": gov_audit.get("jurisdiction"),
                            "confidence": gov_audit.get("confidence"),
                            "lawful_basis": gov_audit.get("lawful_basis"),
                            "retention_days": gov_audit.get("retention_days"),
                            "counts": gov_audit.get("counts")
                        })
                    else:
                        st.info("No governance audit available.")
                with col2:
                    st.markdown("**🚀 Reinforcement Audit**")
                    reinf_audit = (res["reinf"] or {}).get("audit") if res.get("reinf") else None
                    if reinf_audit: st.json(reinf_audit)
                    else: st.info("No reinforcement audit yet.")
                if redacts:
                    st.markdown("**🔒 Redaction Details**")
                    df_r = pd.DataFrame(redacts)
                    st.dataframe(df_r, width='stretch', height=240)

    
    # Footer
    st.markdown("<br/>", unsafe_allow_html=True)
   
    st.markdown('<div class="su-glass" style="text-align:center;">🚀 <strong>SureSight AI</strong> • Agentic/Privacy-first document intelligence</div>', unsafe_allow_html=True)

# ===================== Hooks (optional) =====================
components.html("<script>window.addEventListener('message', (e)=>{ if(!e.data)return; if(e.data.type==='streamlit:refreshHealth'){location.reload();}});</script>", height=0)

render_app()
