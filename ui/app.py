# # app.py
# import os, json, base64, httpx, time
# from dotenv import load_dotenv
# import streamlit as st
# import pandas as pd

# load_dotenv()

# # ===================== Service endpoints =====================
# OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
# GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
# REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# # ===================== Asset paths (logos) =====================
# LEFT_LOGO  = r"C:\Users\ParthSurydhwaj\Downloads\ADROSONIC LOGO BLACK.png"
# RIGHT_LOGO = "static/logo-right.png"
# BRAND_LOGO = "static/suresight-logo.png"

# # ===================== Page config =====================
# st.set_page_config(page_title="SureSight AI • Agentic OCR", layout="wide", initial_sidebar_state="expanded")

# # ===================== Global Style (Futuristic / Glass) =====================
# STYLES = """
# <style>
# :root{
#   --bg:#0a0f1e; --panel:#0e1430; --glass:rgba(255,255,255,0.06);
#   --edge:rgba(255,255,255,0.12); --text:#e6e9f5; --muted:#9aa4bf; --accent:#7dd3fc;
#   --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --chip:#11183b; --chipb:#1c2553;
# }
# html, body, [data-testid="stAppViewContainer"] {
#   background: radial-gradient(1200px 600px at 20% 0%, #0f1a3c 0%, #0a0f1e 45%, #070b18 100%) !important;
# }
# .block-container {padding-top: .8rem; padding-bottom: 2rem; max-width: 1400px;}
# * { color: var(--text); }
# a { color: var(--accent); }
# .su-surface { background: linear-gradient(160deg, var(--panel) 0%, #0c1233 100%);
#               border: 1px solid var(--edge); border-radius: 18px; padding: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset;}
# .su-glass { background: var(--glass); border: 1px solid var(--edge); border-radius: 18px; padding: 18px; backdrop-filter: blur(10px);}
# .su-chip { display:inline-flex; align-items:center; gap:.5rem; padding:6px 12px; border-radius:999px; background:linear-gradient(160deg,var(--chip),var(--chipb)); border:1px solid var(--edge); font-size:.85rem; }
# .su-dot {width:10px; height:10px; border-radius:50%;}
# .ok {background: var(--ok);} .warn{background:var(--warn);} .bad{background:var(--bad);}
# .su-header {
#   border-radius: 22px; padding: 28px;
#   background: conic-gradient(from 220deg at 10% 10%, #1f3b8a, #0ea5e9, #673ab7, #0ea5e9, #1f3b8a);
#   box-shadow: 0 20px 80px rgba(14, 165, 233, .25);
# }
# .su-head-inner {display:flex; align-items:center; justify-content:space-between;}
# .brand {display:flex; align-items:center; gap:14px;}
# .brand img {height:44px;}
# .brand h1 {margin:0; font-weight:800; letter-spacing:.6px;}
# .brand-sub {margin:0; opacity:0.92;}
# .hero {text-align:center; padding:48px 24px;}
# .hero h1 {font-size:2.6rem; margin-bottom:.25rem; font-weight:900;}
# .hero p {color:#dbeafe; opacity:.95; margin-top:.25rem;}
# .cta-row {display:flex; gap:12px; justify-content:center; margin-top:20px;}
# .cta {background: #11183b; border:1px solid var(--edge); padding:10px 16px; border-radius:12px; cursor:pointer;}
# .cta-primary {background:linear-gradient(160deg,#2563eb,#0ea5e9); border:none; }
# footer {visibility:hidden;}
# /* Sanitized text */
# .sanitized-shell { border-radius:16px; overflow:hidden; border:1px solid var(--edge); }
# .sanitized-bar { display:flex; gap:10px; align-items:center; padding:10px 12px; background:linear-gradient(160deg,#0b122e,#0f1844); border-bottom:1px solid var(--edge);}
# .sanitized-body { background: #0a0f1e; padding:14px; max-height:420px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; line-height:1.55; }
# .redacted { background: rgba(239,68,68,.15); border: 1px dashed rgba(239,68,68,.5); padding: 2px 6px; border-radius:6px; color:#fecaca; }
# .kv {display:grid; grid-template-columns: 160px 1fr; gap:10px; }
# .stat {text-align:center; background: var(--glass); border:1px solid var(--edge); border-radius:14px; padding:10px;}
# .metric {font-size:1.15rem; font-weight:800;}
# /* Sidebar agent panel */
# .sidebar-title {font-weight:700; margin-bottom:.2rem;}
# .agent-card {border:1px solid var(--edge); border-radius:14px; padding:12px; margin-bottom:12px; background:var(--glass);}
# .agent-row {display:flex; align-items:center; justify-content:space-between;}
# .agent-name {font-weight:600;}
# .agent-step {color:var(--muted); font-size:.85rem;}
# .progress-wrap {height:6px; background:#10193b; border-radius:999px; overflow:hidden; margin-top:8px;}
# .progress-inner {height:100%; background:linear-gradient(90deg,#22d3ee,#60a5fa,#a78bfa); width:0%;}
# /* Tabs */
# .stTabs [data-baseweb="tab-list"] {gap: 8px;}
# .stTabs [data-baseweb="tab"] {padding: 10px 18px; border-radius: 10px 10px 0 0; background: #0e1534; border: 1px solid var(--edge);}
# .stTabs [aria-selected="true"] {background: linear-gradient(160deg,#1e293b,#0b122e); color: white; border-bottom-color: transparent;}
# /* Buttons */
# .stButton>button, .stDownloadButton>button { border-radius:12px; }
# .stSpinner > div > div {border-color: #38bdf8 transparent transparent transparent;}
# </style>
# """
# st.markdown(STYLES, unsafe_allow_html=True)

# # ===================== App State =====================
# if "phase" not in st.session_state:
#     st.session_state.phase = "intro"  # intro -> app
# if "agent_state" not in st.session_state:
#     st.session_state.agent_state = {
#         "OCR": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
#         "Gov": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
#         "Reinf": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
#     }
# if "last_health" not in st.session_state:
#     st.session_state.last_health = {}
# # Results
# for k in ["job_id","ocr_result","gov_result","reinf_result","final_view","role","redacts","gov_audit"]:
#     if k not in st.session_state:
#         st.session_state[k] = None

# # ===================== Helpers =====================
# def b64_for_uploaded(file):
#     file.seek(0)
#     return base64.b64encode(file.read()).decode("utf-8")

# def metrics_from(ocr: dict):
#     words = len((ocr.get("full_text") or "").split())
#     ents  = len(ocr.get("entities") or [])
#     tabs  = len(ocr.get("tables") or [])
#     conf  = float(ocr.get("confidence") or 0.0)
#     cls   = ocr.get("doc_class","unknown")
#     return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

# def fmt_sanitized_html(text, redaction_count, policy_version, role):
#     if not text:
#         text = "No text content available."
#     safe_html = (
#         text.replace("&","&amp;")
#             .replace("<","&lt;")
#             .replace(">", "&gt;")
#             .replace("[REDACTED]", '<span class="redacted">[REDACTED]</span>')
#     )
#     toolbar = f"""
#     <div class="sanitized-bar">
#       <span class="su-chip"><span class="su-dot ok"></span> Sanitized View</span>
#       <span class="su-chip">Role: <strong>{role}</strong></span>
#       <span class="su-chip">Policy: {policy_version}</span>
#       <span class="su-chip">Redactions: <strong>{redaction_count}</strong></span>
#     </div>
#     """
#     body = f'<div class="sanitized-body">{safe_html}</div>'
#     return f'<div class="sanitized-shell">{toolbar}{body}</div>'

# def ping_health():
#     try:
#         with httpx.Client(timeout=5) as cli:
#             return {
#                 "OCR": cli.get(f"{OCR_URL}/health").json(),
#                 "Gov": cli.get(f"{GOV_URL}/health").json(),
#                 "Reinf": cli.get(f"{REINF_URL}/health").json(),
#             }
#     except Exception:
#         return {}

# def set_agent(key, status=None, pct=None, tone=None, step=None):
#     cur = st.session_state.agent_state.get(key, {})
#     if status is not None: cur["status"]=status
#     if pct is not None: cur["pct"]=pct
#     if tone is not None: cur["tone"]=tone
#     if step is not None: cur["step"]=step
#     st.session_state.agent_state[key]=cur

# def agent_panel():
#     st.sidebar.markdown("### ⚙️ Agents")
#     st.sidebar.caption("Live status while your document is processed.")
#     for label, key, icon in [("OCR Engine","OCR","🔤"), ("Governance","Gov","🛡️"), ("Reinforcement","Reinf","🚀")]:
#         state = st.session_state.agent_state.get(key, {})
#         st.sidebar.markdown(f"""
#         <div class="agent-card">
#           <div class="agent-row">
#             <div class="agent-name">{icon} {label}</div>
#             <div class="su-chip"><span class="su-dot {'ok' if state.get('tone')=='ok' else 'warn' if state.get('tone')=='warn' else 'bad'}"></span>{state.get('status','')}</div>
#           </div>
#           <div class="agent-step">{state.get('step','')}</div>
#           <div class="progress-wrap"><div class="progress-inner" style="width:{int(state.get('pct',0))}%;"></div></div>
#         </div>
#         """, unsafe_allow_html=True)

#     # Health
#     st.sidebar.markdown("### 🌐 Services")
#     if st.sidebar.button("Refresh health", use_container_width=True):
#         st.session_state.last_health = ping_health()
#     if not st.session_state.last_health:
#         st.session_state.last_health = ping_health()
#     cols = st.sidebar.columns(3)
#     for i,(label,key) in enumerate([("OCR","OCR"),("Gov","Gov"),("Reinf","Reinf")]):
#         ok = bool(st.session_state.last_health.get(key,{}).get("ok", False))
#         tone = "ok" if ok else "bad"
#         cols[i].markdown(
#             f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}</span>',
#             unsafe_allow_html=True
#         )

# # ===================== Header =====================
# def top_header():
#     st.markdown(f"""
#     <div class="su-header">
#       <div class="su-head-inner">
#         <div class="brand">
#           <img src='{LEFT_LOGO}' onerror="this.style.display='none';this.insertAdjacentText('afterend','🔍');"/>
#           <h1>SureSight AI</h1>
#         </div>
#         <div class="brand">
#           <p class="brand-sub">Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • HIPAA/GDPR Ready</p>
#         </div>
#         <div class="brand">
#           <img src='{RIGHT_LOGO}' onerror="this.style.display='none';this.insertAdjacentText('afterend','🛡️');"/>
#         </div>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

# # ===================== Intro Screen =====================
# def render_intro():
#     top_header()
#     st.markdown(f"""
#     <div class="su-surface hero">
#       <img src='{BRAND_LOGO}' style="height:56px;opacity:.95;" onerror="this.style.display='none';">
#       <h1>Welcome to SureSight AI</h1>
#       <p>Futuristic, privacy-first document intelligence. Upload, govern, and trust your data—end to end.</p>
#       <div class="cta-row">
#         <button class="cta cta-primary" onclick="window.parent.postMessage({{type:'streamlit:setPhase', phase:'app'}}, '*')">Get Started</button>
#         <button class="cta" onclick="window.parent.postMessage({{type:'streamlit:refreshHealth'}}, '*')">Check Services</button>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Fallback buttons
#     c1, c2 = st.columns([0.35,0.65])
#     with c1:
#         if st.button("🚀 Enter Workspace", use_container_width=True):
#             st.session_state.phase = "app"; st.rerun()
#     with c2:
#         if st.button("🔄 Refresh Health", use_container_width=True):
#             st.session_state.last_health = ping_health()
#             st.success("Health refreshed")

#     # Mini highlights
#     c1,c2,c3 = st.columns(3)
#     with c1:
#         st.markdown('<div class="su-glass stat"><div>🔒 Compliance-first</div><div class="metric">GDPR / HIPAA</div></div>', unsafe_allow_html=True)
#     with c2:
#         st.markdown('<div class="su-glass stat"><div>⚡ Agentic Workflow</div><div class="metric">OCR → Govern → Reinforce</div></div>', unsafe_allow_html=True)
#     with c3:
#         st.markdown('<div class="su-glass stat"><div>🧠 Multimodal</div><div class="metric">Gemini 2.5 Flash</div></div>', unsafe_allow_html=True)

# # ===================== Main App (Workspace) =====================
# def render_app():
#     top_header()
#     agent_panel()

#     st.markdown("#### 🧪 Workspace")
#     with st.container():
#         c1,c2,c3,c4 = st.columns([0.42,0.19,0.19,0.20])
#         with c1:
#             uploaded = st.file_uploader(
#                 "📄 Upload Document (PNG / JPG)",
#                 type=["png","jpg","jpeg"],
#                 help="Upload an image (PNG/JPG)."
#             )
#         with c2:
#             role = st.selectbox("👤 User Role", ["admin","client"], index=1, help="Admin: raw OCR; Client: sanitized")
#         with c3:
#             human_req = st.selectbox("🎯 Task Type", ["extract (default)","translate","summarize"], index=0)
#         with c4:
#             target_locale = st.selectbox("🌍 Locale", ["en-IN","hi-IN","en-US","fr-FR"], index=0)

#     run_col, info_col = st.columns([0.25, 0.75])
#     with run_col:
#         run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)
#     with info_col:
#         if uploaded: st.success(f"✅ Ready to process: {uploaded.name}")
#         else: st.info("📋 Upload a PNG/JPG to begin processing")

#     # Quick service chips
#     hc = st.columns(3)
#     health = ping_health()
#     for i,(label,key) in enumerate([("OCR","OCR"),("Governance","Gov"),("Reinforcement","Reinf")]):
#         ok = bool(health.get(key,{}).get("ok", False))
#         tone = "ok" if ok else "bad"
#         hc[i].markdown(f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}: {"Online" if ok else "Offline"}</span>', unsafe_allow_html=True)

#     # ========== Run Pipeline ==========
#     if run:
#         if not uploaded:
#             st.error("⚠️ Please upload a PNG/JPG first.")
#             st.stop()

#         st.session_state.role = role
#         job_id = f"job-{int(time.time())}"
#         st.session_state.job_id = job_id

#         # Progress UI (sidebar)
#         for k in ["OCR","Gov","Reinf"]:
#             set_agent(k, status="Queued", pct=0, tone="warn", step="Queued")

#         img_b64 = b64_for_uploaded(uploaded)

#         progress_bar = st.progress(0)
#         status_text = st.empty()

#         # ---- OCR ----
#         set_agent("OCR", status="Running", pct=20, tone="warn", step=f"Reading {uploaded.name}")
#         status_text.text("🔤 Processing OCR…")
#         progress_bar.progress(20)
#         try:
#             with httpx.Client(timeout=180) as cli:
#                 ocr = cli.post(f"{OCR_URL}/a2a/ocr", json={
#                     "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
#                     "input":{"page_images_b64": [img_b64], "hints":{"locale": target_locale}}
#                 }, timeout=180.0).json()
#         except Exception as e:
#             set_agent("OCR", status="Error", pct=0, tone="bad", step="Failed to call OCR")
#             st.exception(e); st.stop()

#         set_agent("OCR", status="Complete", pct=40, tone="ok", step="Text extracted")

#         # ---- Governance ----
#         set_agent("Gov", status="Running", pct=55, tone="warn", step="Applying rules")
#         status_text.text("🛡️ Applying governance rules…")
#         progress_bar.progress(55)
#         try:
#             with httpx.Client(timeout=90) as cli:
#                 gov = cli.post(f"{GOV_URL}/a2a/govern", json={
#                     "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
#                     "input":{
#                         "ocr_result": ocr,
#                         "viewer": {"role": role},
#                         "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#                         "lawful_basis": "contract",
#                         "retention_days": 365
#                     }
#                 }, timeout=90.0).json()
#         except Exception as e:
#             set_agent("Gov", status="Error", pct=55, tone="bad", step="Governance error")
#             st.exception(e); st.stop()

#         set_agent("Gov", status="Complete", pct=80, tone="ok", step="Sanitized view generated")
#         progress_bar.progress(80)
#         status_text.text("✅ OCR & Governance complete")

#         # Save results in session
#         st.session_state.ocr_result = ocr
#         st.session_state.gov_result = gov
#         st.session_state.reinf_result = None  # reset any previous reinforcement
#         sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
#         st.session_state.final_view = sanitized
#         st.session_state.redacts = gov.get("redaction_manifest", []) or []
#         st.session_state.gov_audit = gov.get("audit", {}) or {}

#         # Finish progress
#         set_agent("Reinf", status="Idle", pct=80, tone="warn", step="Awaiting feedback")
#         progress_bar.progress(100); status_text.text("🧷 Provide reinforcement feedback in the Reinforcement tab.")
#         time.sleep(0.5); progress_bar.empty(); status_text.empty()

#     # ========== If we have results, render dashboards ==========
#     if st.session_state.ocr_result and st.session_state.final_view:
#         ocr = st.session_state.ocr_result
#         final_view = st.session_state.final_view
#         gov = st.session_state.gov_result or {}
#         redacts = st.session_state.redacts or []
#         gov_audit = st.session_state.gov_audit or {}
#         role = st.session_state.role or "client"

#         # Metrics
#         m = metrics_from(ocr)
#         st.markdown("### 📊 Document Analysis")
#         mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
#         with mcol1:
#             st.markdown(f'<div class="su-glass stat">📄<div>Document Type</div><div class="metric">{m["doc_class"]}</div></div>', unsafe_allow_html=True)
#         with mcol2:
#             color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
#             st.markdown(f'<div class="su-glass stat">{color}<div>Confidence</div><div class="metric">{m["confidence"]:.2f}</div></div>', unsafe_allow_html=True)
#         with mcol3:
#             st.markdown(f'<div class="su-glass stat">📝<div>Words</div><div class="metric">{m["words"]:,}</div></div>', unsafe_allow_html=True)
#         with mcol4:
#             st.markdown(f'<div class="su-glass stat">🏷️<div>Entities</div><div class="metric">{m["entities"]}</div></div>', unsafe_allow_html=True)
#         with mcol5:
#             st.markdown(f'<div class="su-glass stat">📊<div>Tables</div><div class="metric">{m["tables"]}</div></div>', unsafe_allow_html=True)

#         # Pull last reinforcement state up-front for badges/reasons
#         reinf = st.session_state.reinf_result or {}
#         reinf_status = reinf.get("status")
#         reinf_audit = (reinf.get("audit") or {}) if reinf else {}
#         reinf_reason = reinf_audit.get("reason")
#         raw_sample = reinf_audit.get("raw_model_sample")

#         # Tabs
#         if role == "admin":
#             tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🔍 Raw OCR", "🚀 Reinforcement", "📋 Audit"]
#             idx_raw, idx_reinf, idx_audit = 3, 4, 5
#         else:
#             tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🚀 Reinforcement", "📋 Audit"]
#             idx_reinf, idx_audit = 3, 4
#         tabs = st.tabs(tab_labels)

#         # Final View
#         with tabs[0]:
#             st.markdown("#### 🔒 Final View")
#             html = fmt_sanitized_html(
#                 final_view.get("full_text",""),
#                 len(redacts),
#                 gov.get("policy_version","N/A"),
#                 role
#             )
#             st.markdown(html, unsafe_allow_html=True)

#             # Reinforcement status badge + reason
#             if reinf_status:
#                 if reinf_status == "ok":
#                     applied = bool(reinf_audit.get("applied_feedback"))
#                     badge = "✅ Reinforcement Applied" if applied else "ℹ️ No Changes Needed"
#                     st.markdown(f'<span class="su-chip"><span class="su-dot ok"></span>{badge}</span>', unsafe_allow_html=True)
#                 elif reinf_status == "skipped":
#                     msg = reinf_reason or "Skipped by user or policy."
#                     st.markdown(f'<span class="su-chip"><span class="su-dot warn"></span>⏭️ Reinforcement Skipped</span> — {msg}', unsafe_allow_html=True)
#                 else:
#                     msg = reinf_reason or (reinf.get("detail") or "Unknown error")
#                     st.markdown(f'<span class="su-chip"><span class="su-dot bad"></span>⚠️ Reinforcement Error</span> — {msg}', unsafe_allow_html=True)
#                 if raw_sample:
#                     with st.expander("🔎 Model Output Sample (truncated)"):
#                         st.code(raw_sample, language="json")

#             st.download_button(
#                 "⬇️ Download Final Text",
#                 data=(final_view.get("full_text") or "").encode("utf-8"),
#                 file_name=f"{st.session_state.job_id or 'job'}-final.txt",
#                 mime="text/plain",
#                 use_container_width=True
#             )

#         # Entities
#         with tabs[1]:
#             st.markdown("#### 🏷️ Entities (Final)")
#             ents = final_view.get("entities", []) or []
#             if ents:
#                 df = pd.DataFrame(ents)
#                 if 'redacted' in df.columns:
#                     df['visibility'] = df['redacted'].map({True:'🔒 Protected', False:'👁️ Visible'})
#                 st.dataframe(df, use_container_width=True, height=320)
#                 st.caption(f"📊 {len(ents)} entities • Privacy & feedback applied")
#             else:
#                 st.info("🔍 No entities detected.")

#         # Tables
#         with tabs[2]:
#             st.markdown("#### 📊 Document Tables (Final)")
#             tables = final_view.get("tables", []) or []
#             if tables:
#                 for i,t in enumerate(tables):
#                     with st.expander(f"📋 Table {i+1}: {t.get('id','Unnamed')}", expanded=(i==0)):
#                         rows = t.get("rows", []) or []
#                         if rows:
#                             try:
#                                 header, *data = rows if len(rows) > 1 else ([], rows)
#                                 if header and data and all(len(r) == len(header) for r in data):
#                                     df = pd.DataFrame(data, columns=header)
#                                 else:
#                                     df = pd.DataFrame(rows)
#                                 st.dataframe(df, use_container_width=True, height=240)
#                             except Exception:
#                                 st.dataframe(pd.DataFrame(rows), use_container_width=True, height=240)
#                         else:
#                             st.info("📝 Empty table.")
#             else:
#                 st.info("📊 No tables detected.")

#         # Raw OCR (Admin)
#         if role == "admin" and len(tabs) > 3:
#             with tabs[idx_raw]:
#                 st.markdown("#### 🔍 Raw OCR Output")
#                 st.info("👨‍💼 Admin view: Unfiltered OCR results")
#                 st.json(ocr)

#         # Reinforcement (form + audit + result)
#         with tabs[idx_reinf]:
#             st.markdown("#### 🚀 Reinforcement: Human Feedback & Final Output")

#             if not st.session_state.gov_result:
#                 st.info("Run the pipeline first to enable reinforcement.")
#             else:
#                 with st.form("reinforcement_form", clear_on_submit=False):
#                     apply_flag = st.checkbox("Apply reinforcement", value=True, help="Use Gemini to apply your feedback safely.")
#                     placeholder_hint = "e.g., Standardize dates to YYYY-MM-DD, normalize currency to INR, fix mislabeled columns."
#                     feedback_text = st.text_area("📝 Your Feedback", height=120, placeholder=placeholder_hint)
#                     submitted = st.form_submit_button("Apply Feedback")

#                 if submitted:
#                     set_agent("Reinf", status="Running", pct=85, tone="warn", step="Optimizing outputs")
#                     try:
#                         with httpx.Client(timeout=90) as cli:
#                             reinf = cli.post(f"{REINF_URL}/a2a/reinforce", json={
#                                 "protocol":"a2a.v1","intent":"doc.reinforce","job_id":st.session_state.job_id or f"job-{int(time.time())}",
#                                 "input":{
#                                     "apply": bool(apply_flag),
#                                     "feedback": feedback_text or "",
#                                     "governance_result": st.session_state.gov_result,
#                                     "viewer": {"role": role},
#                                     "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#                                     "lawful_basis": "contract",
#                                     "retention_days": 365
#                                 }
#                             }, timeout=90.0).json()
#                         st.session_state.reinf_result = reinf

#                         r_status = reinf.get("status")
#                         r_audit  = reinf.get("audit") or {}
#                         r_reason = r_audit.get("reason")

#                         if r_status == "ok":
#                             # Update final view to model-merged output
#                             st.session_state.final_view = reinf.get("final") or st.session_state.final_view
#                             set_agent("Reinf", status="Complete", pct=100, tone="ok",
#                                       step="Applied" if r_audit.get("applied_feedback") else "No changes")
#                             st.success("Reinforcement applied." if r_audit.get("applied_feedback") else "No changes were necessary.")
#                             st.rerun()
#                         elif r_status == "skipped":
#                             set_agent("Reinf", status="Skipped", pct=90, tone="warn",
#                                       step=f"Skipped: {r_reason or 'see audit'}")
#                             st.info(f"Reinforcement skipped. Reason: {r_reason or 'apply=false or policy/LLM constraint.'}")
#                         else:
#                             msg = r_reason or (reinf.get("detail") or "Unknown error")
#                             set_agent("Reinf", status="Error", pct=90, tone="bad", step=f"Error: {msg}")
#                             st.error(msg)
#                     except Exception as e:
#                         set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent call failed")
#                         st.exception(e)

#             # Show last reinforcement audit/result (if any)
#             reinf = st.session_state.reinf_result or {}
#             if reinf:
#                 st.markdown("**Status & Audit**")
#                 st.json({
#                     "status": reinf.get("status"),
#                     "applied_feedback": (reinf.get("audit") or {}).get("applied_feedback"),
#                     "reason": (reinf.get("audit") or {}).get("reason"),
#                     "model": (reinf.get("audit") or {}).get("model"),
#                     "sdk": (reinf.get("audit") or {}).get("sdk"),
#                     "latency_ms_total": (reinf.get("audit") or {}).get("latency_ms_total"),
#                     "timestamp": (reinf.get("audit") or {}).get("timestamp")
#                 })
#                 raw_sample = (reinf.get("audit") or {}).get("raw_model_sample")
#                 if raw_sample:
#                     with st.expander("🔎 Model Output Sample (truncated)"):
#                         st.code(raw_sample, language="json")
#                 st.markdown("**📦 Final JSON**")
#                 st.json(st.session_state.final_view)

#         # Audit tab
#         with tabs[idx_audit]:
#             st.markdown("#### 📋 Compliance Audit Trail")
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.markdown("**🕒 Governance Audit**")
#                 if gov_audit:
#                     st.json({
#                         "timestamp": gov_audit.get("timestamp"),
#                         "viewer_role": gov_audit.get("viewer_role"),
#                         "jurisdiction": gov_audit.get("jurisdiction"),
#                         "confidence": gov_audit.get("confidence"),
#                         "lawful_basis": gov_audit.get("lawful_basis"),
#                         "retention_days": gov_audit.get("retention_days"),
#                         "counts": gov_audit.get("counts")
#                     })
#                 else:
#                     st.info("No governance audit available.")
#             with col2:
#                 st.markdown("**🚀 Reinforcement Audit**")
#                 reinf_audit = (st.session_state.reinf_result or {}).get("audit") if st.session_state.reinf_result else None
#                 if reinf_audit:
#                     st.json(reinf_audit)
#                 else:
#                     st.info("No reinforcement audit yet.")
#             if redacts:
#                 st.markdown("**🔒 Redaction Details**")
#                 df_r = pd.DataFrame(redacts)
#                 st.dataframe(df_r, use_container_width=True, height=240)

#     # Closing panel
#     st.markdown("<br/>", unsafe_allow_html=True)
#     st.markdown(
#         '<div class="su-glass" style="text-align:center;">'
#         '🚀 <strong>SureSight AI</strong> • Futuristic, privacy-first document intelligence'
#         '</div>',
#         unsafe_allow_html=True
#     )

# # ===================== Router (JS hooks for intro buttons) =====================
# st.components.v1.html("""
# <script>
# window.addEventListener('message', (e)=>{
#   if(!e.data) return;
#   if(e.data.type==='streamlit:setPhase'){
#     const data = {"phase": e.data.phase};
#     window.parent.postMessage({isStreamlitMessage:true, type:'SET_COMPONENT_VALUE', value: data}, '*');
#   }
#   if(e.data.type==='streamlit:refreshHealth'){
#     location.reload();
#   }
# });
# </script>
# """, height=0)

# # ===================== Phase Switch =====================
# if st.session_state.phase == "intro":
#     render_intro()
# else:
#     render_app()



################SureSight AI - Document Intelligence Platform################
import os, json, base64, httpx, time, difflib
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

load_dotenv()

# ===================== Service endpoints =====================
OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# ===================== Asset paths (logos) =====================
LEFT_LOGO  = r"C:\\Users\\ParthSurydhwaj\\Downloads\\ADROSONIC LOGO BLACK.png"
RIGHT_LOGO = r"C:\Users\ParthSurydhwaj\Downloads\DIL Logo.png"
BRAND_LOGO = "static/suresight-logo.png"

# ===================== Page config =====================
st.set_page_config(page_title="SureSight AI • Agentic OCR", layout="wide", initial_sidebar_state="expanded")

# ===================== Global Style (Navy theme + higher-contrast buttons) =====================
STYLES = """
<style>
:root{
  /* Deep navy palette */
  --bg:#071225; --panel:#0b1730; --glass:rgba(255,255,255,0.05);
  --edge:rgba(255,255,255,0.12); --text:#eaf2ff; --muted:#9bb3d8; --accent:#5ee7ff;
  --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --chip:#0b1838; --chipb:#14265a;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 20% 0%, #0c1b3f 0%, #08122a 45%, #061026 100%) !important;
}
.block-container {padding-top: .8rem; padding-bottom: 2rem; max-width: 1400px;}
* { color: var(--text); }
a { color: var(--accent); }

/* Surfaces */
.su-surface { background: linear-gradient(160deg, var(--panel) 0%, #0c1436 100%);
              border: 1px solid var(--edge); border-radius: 18px; padding: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset;}
.su-glass { background: var(--glass); border: 1px solid var(--edge); border-radius: 18px; padding: 18px; backdrop-filter: blur(10px);}  
.su-chip { display:inline-flex; align-items:center; gap:.5rem; padding:6px 12px; border-radius:999px; background:linear-gradient(160deg,var(--chip),var(--chipb)); border:1px solid var(--edge); font-size:.85rem; }
.su-dot {width:10px; height:10px; border-radius:50%;}
.ok {background: var(--ok);} .warn{background:var(--warn);} .bad{background:var(--bad);} 

/* Header */
.su-header {
  border-radius: 22px; padding: 28px;
  background: conic-gradient(from 220deg at 10% 10%, #18306f, #0ea5e9, #5b21b6, #0ea5e9, #18306f);
  box-shadow: 0 20px 80px rgba(14, 165, 233, .25);
}
.su-head-inner {display:flex; align-items:center; justify-content:space-between;}
.brand {display:flex; align-items:center; gap:14px;}
.brand img {display:none;}
.logos{display:flex; gap:16px; align-items:center;}
.logos img{height:56px;}
.brand h1 {margin:0; font-weight:800; letter-spacing:.6px;}
.brand-sub {margin:0; opacity:0.92;}

/* Hero */
.hero {text-align:center; padding:48px 24px;}
.hero h1 {font-size:2.6rem; margin-bottom:.25rem; font-weight:900;}
.hero p {color:#dbeafe; opacity:.95; margin-top:.25rem;}
.cta-row {display:flex; gap:12px; justify-content:center; margin-top:20px;}
.cta {color:#fff; background: linear-gradient(160deg,#1d4ed8,#0ea5e9); border:1px solid rgba(255,255,255,0.12); padding:10px 16px; border-radius:12px; cursor:pointer; box-shadow:0 6px 20px rgba(14,165,233,.25);} 
.cta:hover{filter:brightness(1.05);} 
.cta-primary {background:linear-gradient(160deg,#0ea5e9,#22d3ee);} 

/* Footer */
footer {visibility:hidden;}

/* Sanitized text */
.sanitized-shell { border-radius:16px; overflow:hidden; border:1px solid var(--edge); }
.sanitized-bar { display:flex; gap:10px; align-items:center; padding:10px 12px; background:linear-gradient(160deg,#0b1436,#0e1a4b); border-bottom:1px solid var(--edge);} 
.sanitized-body { background: #071225; padding:14px; max-height:420px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; line-height:1.55; }
.redacted { background: rgba(239,68,68,.15); border: 1px dashed rgba(239,68,68,.5); padding: 2px 6px; border-radius:6px; color:#fecaca; }
.kv {display:grid; grid-template-columns: 160px 1fr; gap:10px; }
.stat {text-align:center; background: var(--glass); border:1px solid var(--edge); border-radius:14px; padding:10px;}
.metric {font-size:1.15rem; font-weight:800;}

/* Sidebar agent panel */
.sidebar-title {font-weight:700; margin-bottom:.2rem;}
.agent-card {border:1px solid var(--edge); border-radius:14px; padding:12px; margin-bottom:12px; background:var(--glass);} 
.agent-row {display:flex; align-items:center; justify-content:space-between;}
.agent-name {font-weight:600;}
.agent-step {color:var(--muted); font-size:.85rem;}
.progress-wrap {height:6px; background:#0e1d4d; border-radius:999px; overflow:hidden; margin-top:8px;}
.progress-inner {height:100%; background:linear-gradient(90deg,#22d3ee,#60a5fa,#a78bfa); width:0%;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {padding: 10px 18px; border-radius: 10px 10px 0 0; background: #0e1534; border: 1px solid var(--edge);} 
.stTabs [aria-selected="true"] {background: linear-gradient(160deg,#172554,#0b122e); color: white; border-bottom-color: transparent; box-shadow: 0 10px 30px rgba(0,0,0,.25) inset;}

/* HIGHER-CONTRAST Streamlit buttons */
.stButton>button, .stDownloadButton>button { 
  background: linear-gradient(160deg,#1d4ed8,#0ea5e9) !important; 
  color: #ffffff !important; border: 1px solid rgba(255,255,255,0.12) !important; 
  border-radius:12px !important; box-shadow: 0 6px 20px rgba(14,165,233,.25) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover { filter: brightness(1.06); transform: translateY(-1px); }
.stButton>button:focus, .stDownloadButton>button:focus { outline: 2px solid rgba(94,231,255,.35); }
.stButton>button:disabled, .stDownloadButton>button:disabled { background: #2a3c70 !important; color:#e5ecff !important; opacity: .8; }

/* Spinner color tweak */
.stSpinner > div > div {border-color: #38bdf8 transparent transparent transparent;}
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

# ===================== App State =====================
if "phase" not in st.session_state:
    st.session_state.phase = "intro"  # intro -> app
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "OCR": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
        "Gov": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
        "Reinf": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
    }
if "last_health" not in st.session_state:
    st.session_state.last_health = {}
# Results
for k in ["job_id","ocr_result","gov_result","reinf_result","final_view","role","redacts","gov_audit","pre_reinf_view"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ===================== Helpers =====================
def b64_for_uploaded(file):
    file.seek(0)
    return base64.b64encode(file.read()).decode("utf-8")

def metrics_from(ocr: dict):
    words = len((ocr.get("full_text") or "").split())
    ents  = len(ocr.get("entities") or [])
    tabs  = len(ocr.get("tables") or [])
    conf  = float(ocr.get("confidence") or 0.0)
    cls   = ocr.get("doc_class","unknown")
    return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

def fmt_sanitized_html(text, redaction_count, policy_version, role):
    if not text:
        text = "No text content available."
    safe_html = (text.replace("&","&amp;").replace("<","&lt;").replace(">", "&gt;").replace("[REDACTED]", '<span class="redacted">[REDACTED]</span>'))
    toolbar = f"""
    <div class="sanitized-bar">
      <span class="su-chip"><span class="su-dot ok"></span> Sanitized View</span>
      <span class="su-chip">Role: <strong>{role}</strong></span>
      <span class="su-chip">Policy: {policy_version}</span>
      <span class="su-chip">Redactions: <strong>{redaction_count}</strong></span>
    </div>
    """
    body = f'<div class="sanitized-body">{safe_html}</div>'
    return f'<div class="sanitized-shell">{toolbar}{body}</div>'

def ping_health():
    try:
        with httpx.Client(timeout=5) as cli:
            return {
                "OCR": cli.get(f"{OCR_URL}/health").json(),
                "Gov": cli.get(f"{GOV_URL}/health").json(),
                "Reinf": cli.get(f"{REINF_URL}/health").json(),
            }
    except Exception:
        return {}

def set_agent(key, status=None, pct=None, tone=None, step=None):
    cur = st.session_state.agent_state.get(key, {})
    if status is not None: cur["status"]=status
    if pct is not None: cur["pct"]=pct
    if tone is not None: cur["tone"]=tone
    if step is not None: cur["step"]=step
    st.session_state.agent_state[key]=cur

def agent_panel():
    st.sidebar.markdown("### ⚙️ Agents")
    st.sidebar.caption("Live status while your document is processed.")
    for label, key, icon in [("OCR Engine","OCR","🔤"), ("Governance","Gov","🛡️"), ("Reinforcement","Reinf","🚀")]:
        state = st.session_state.agent_state.get(key, {})
        st.sidebar.markdown(f"""
        <div class="agent-card">
          <div class="agent-row">
            <div class="agent-name">{icon} {label}</div>
            <div class="su-chip"><span class="su-dot {'ok' if state.get('tone')=='ok' else 'warn' if state.get('tone')=='warn' else 'bad'}"></span>{state.get('status','')}</div>
          </div>
          <div class="agent-step">{state.get('step','')}</div>
          <div class="progress-wrap"><div class="progress-inner" style="width:{int(state.get('pct',0))}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    # Health
    st.sidebar.markdown("### 🌐 Services")
    if st.sidebar.button("Refresh health", use_container_width=True):
        st.session_state.last_health = ping_health()
    if not st.session_state.last_health:
        st.session_state.last_health = ping_health()
    cols = st.sidebar.columns(3)
    for i,(label,key) in enumerate([("OCR","OCR"),("Gov","Gov"),("Reinf","Reinf")]):
        ok = bool(st.session_state.last_health.get(key,{}).get("ok", False))
        tone = "ok" if ok else "bad"
        cols[i].markdown(
            f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}</span>',
            unsafe_allow_html=True
        )

# ===================== Header =====================
def top_header():
    st.markdown(f"""
    <div class=\"su-header\">
      <div class=\"su-head-inner\">
        <div class=\"brand\">
          <h1>SureSight AI</h1>
          <p class=\"brand-sub\">Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • HIPAA/GDPR Ready</p>
        </div>
        <div class=\"logos\">
          <img src='{LEFT_LOGO}' alt=\"Left logo\" onerror=\"this.style.display='none';\"/>
          <img src='{RIGHT_LOGO}' alt=\"Right logo\" onerror=\"this.style.display='none';\"/>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ===================== Intro Screen =====================
def render_intro():
    top_header()
    st.markdown(f"""
    <div class="su-surface hero">
      <img src='{BRAND_LOGO}' style="height:56px;opacity:.95;" onerror="this.style.display='none';">
      <h1>Welcome to SureSight AI</h1>
      <p>Futuristic, privacy-first document intelligence. Upload, govern, and trust your data—end to end.</p>
      <div class="cta-row">
        <button class="cta cta-primary" onclick="window.parent.postMessage({{type:'streamlit:setPhase', phase:'app'}}, '*')">Get Started</button>
        <button class="cta" onclick="window.parent.postMessage({{type:'streamlit:refreshHealth'}}, '*')">Check Services</button>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Fallback buttons
    c1, c2 = st.columns([0.35,0.65])
    with c1:
        if st.button("Enter Workspace", use_container_width=True):
            st.session_state.phase = "app"; st.rerun()
    with c2:
        if st.button("Refresh Health", use_container_width=True):
            st.session_state.last_health = ping_health()
            st.success("Health refreshed")

    # Mini highlights
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="su-glass stat"><div>Compliance-first</div><div class="metric">GDPR / HIPAA</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="su-glass stat"><div>Agentic Workflow</div><div class="metric">OCR → Govern → Reinforce</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="su-glass stat"><div>Multimodal</div><div class="metric">Gemini 2.5 Flash</div></div>', unsafe_allow_html=True)

# ===================== Main App (Workspace) =====================
def render_app():
    top_header()
    agent_panel()

    st.markdown("#### Workspace")
    with st.container():
        c1,c2,c3,c4 = st.columns([0.42,0.19,0.19,0.20])
        with c1:
            uploaded = st.file_uploader(
                "Upload Document (PNG / JPG)",
                type=["png","jpg","jpeg"],
                help="Upload an image (PNG/JPG)."
            )
        with c2:
            role = st.selectbox("User Role", ["admin","client"], index=1, help="Admin: raw OCR; Client: sanitized")
        with c3:
            human_req = st.selectbox("Task Type", ["extract (default)","translate","summarize"], index=0)
        with c4:
            target_locale = st.selectbox("Locale", ["en-IN","hi-IN","en-US","fr-FR"], index=0)

    run_col, info_col = st.columns([0.25, 0.75])
    with run_col:
        run = st.button("Run Pipeline", type="primary", use_container_width=True)
    with info_col:
        if uploaded: st.success(f"Ready to process: {uploaded.name}")
        else: st.info("Upload a PNG/JPG to begin processing")

    # Quick service chips
    hc = st.columns(3)
    health = ping_health()
    for i,(label,key) in enumerate([("OCR","OCR"),("Governance","Gov"),("Reinforcement","Reinf")]):
        ok = bool(health.get(key,{}).get("ok", False))
        tone = "ok" if ok else "bad"
        hc[i].markdown(f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}: {"Online" if ok else "Offline"}</span>', unsafe_allow_html=True)

    # ========== Run Pipeline ==========
    if run:
        if not uploaded:
            st.error("⚠️ Please upload a PNG/JPG first.")
            st.stop()

        st.session_state.role = role
        job_id = f"job-{int(time.time())}"
        st.session_state.job_id = job_id

        # Progress UI (sidebar)
        for k in ["OCR","Gov","Reinf"]:
            set_agent(k, status="Queued", pct=0, tone="warn", step="Queued")

        img_b64 = b64_for_uploaded(uploaded)

        progress_bar = st.progress(0)
        status_text = st.empty()

        # ---- OCR ----
        set_agent("OCR", status="Running", pct=20, tone="warn", step=f"Reading {uploaded.name}")
        status_text.text("Processing OCR…")
        progress_bar.progress(20)
        try:
            with httpx.Client(timeout=180) as cli:
                ocr = cli.post(f"{OCR_URL}/a2a/ocr", json={
                    "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
                    "input":{"page_images_b64": [img_b64], "hints":{"locale": target_locale}}
                }, timeout=180.0).json()
        except Exception as e:
            set_agent("OCR", status="Error", pct=0, tone="bad", step="Failed to call OCR")
            st.exception(e); st.stop()

        set_agent("OCR", status="Complete", pct=40, tone="ok", step="Text extracted")

        # ---- Governance ----
        set_agent("Gov", status="Running", pct=55, tone="warn", step="Applying rules")
        status_text.text("Applying governance rules…")
        progress_bar.progress(55)
        try:
            with httpx.Client(timeout=90) as cli:
                gov = cli.post(f"{GOV_URL}/a2a/govern", json={
                    "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
                    "input":{
                        "ocr_result": ocr,
                        "viewer": {"role": role},
                        "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
                        "lawful_basis": "contract",
                        "retention_days": 365
                    }
                }, timeout=90.0).json()
        except Exception as e:
            set_agent("Gov", status="Error", pct=55, tone="bad", step="Governance error")
            st.exception(e); st.stop()

        set_agent("Gov", status="Complete", pct=80, tone="ok", step="Sanitized view generated")
        progress_bar.progress(80)
        status_text.text("OCR & Governance complete")

        # Save results in session
        st.session_state.ocr_result = ocr
        st.session_state.gov_result = gov
        st.session_state.reinf_result = None  # reset any previous reinforcement
        sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
        st.session_state.final_view = sanitized
        st.session_state.redacts = gov.get("redaction_manifest", []) or []
        st.session_state.gov_audit = gov.get("audit", {}) or {}
        st.session_state.pre_reinf_view = None  # reset

        # Finish progress
        set_agent("Reinf", status="Idle", pct=80, tone="warn", step="Awaiting feedback")
        progress_bar.progress(100); status_text.text("Provide reinforcement feedback in the Reinforcement tab.")
        time.sleep(0.5); progress_bar.empty(); status_text.empty()

    # ========== If we have results, render dashboards ==========
    if st.session_state.ocr_result and st.session_state.final_view:
        ocr = st.session_state.ocr_result
        final_view = st.session_state.final_view
        gov = st.session_state.gov_result or {}
        redacts = st.session_state.redacts or []
        gov_audit = st.session_state.gov_audit or {}
        role = st.session_state.role or "client"

        # Metrics
        m = metrics_from(ocr)
        st.markdown("### 📊 Document Analysis")
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
        with mcol1:
            st.markdown(f'<div class="su-glass stat"><div>Document Type</div><div class="metric">{m["doc_class"]}</div></div>', unsafe_allow_html=True)
        with mcol2:
            color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
            st.markdown(f'<div class="su-glass stat">{color}<div>Confidence</div><div class="metric">{m["confidence"]:.2f}</div></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="su-glass stat"><div>Words</div><div class="metric">{m["words"]:,}</div></div>', unsafe_allow_html=True)
        with mcol4:
            st.markdown(f'<div class="su-glass stat"><div>Entities</div><div class="metric">{m["entities"]}</div></div>', unsafe_allow_html=True)
        with mcol5:
            st.markdown(f'<div class="su-glass stat"><div>Tables</div><div class="metric">{m["tables"]}</div></div>', unsafe_allow_html=True)

        # Pull last reinforcement state up-front for badges/reasons
        reinf = st.session_state.reinf_result or {}
        reinf_status = reinf.get("status")
        reinf_audit = (reinf.get("audit") or {}) if reinf else {}
        reinf_reason = reinf_audit.get("reason")
        raw_sample = reinf_audit.get("raw_model_sample")

        # Tabs
        if role == "admin":
            tab_labels = ["Final View", "Entities", "Tables", "Raw OCR", "Reinforcement", "Audit"]
            idx_raw, idx_reinf, idx_audit = 3, 4, 5
        else:
            tab_labels = ["Final View", "Entities", "Tables", "Reinforcement", "Audit"]
            idx_reinf, idx_audit = 3, 4
        tabs = st.tabs(tab_labels)

        # Final View
        with tabs[0]:
            st.markdown("#### Final View")
            html = fmt_sanitized_html(
                final_view.get("full_text",""),
                len(redacts),
                gov.get("policy_version","N/A"),
                role
            )
            st.markdown(html, unsafe_allow_html=True)

            # Reinforcement status badge + reason
            if reinf_status:
                if reinf_status == "ok":
                    applied = bool(reinf_audit.get("applied_feedback"))
                    badge = "✅ Reinforcement Applied" if applied else "ℹ️ No Changes Needed"
                    st.markdown(f'<span class="su-chip"><span class="su-dot ok"></span>{badge}</span>', unsafe_allow_html=True)
                elif reinf_status == "skipped":
                    msg = reinf_reason or "Skipped by user or policy."
                    st.markdown(f'<span class=\"su-chip\"><span class=\"su-dot warn\"></span>Reinforcement Skipped</span> — {msg}', unsafe_allow_html=True)
                else:
                    msg = reinf_reason or (reinf.get("detail") or "Unknown error")
                    st.markdown(f'<span class=\"su-chip\"><span class=\"su-dot bad\"></span>Reinforcement Error</span> — {msg}', unsafe_allow_html=True)
                if raw_sample:
                    with st.expander("Model Output Sample (truncated)"):
                        st.code(raw_sample, language="json")

            st.download_button(
                "Download Final Text",
                data=(final_view.get("full_text") or "").encode("utf-8"),
                file_name=f"{st.session_state.job_id or 'job'}-final.txt",
                mime="text/plain",
                use_container_width=True
            )

        # Entities
        with tabs[1]:
            st.markdown("#### Entities (Final)")
            ents = final_view.get("entities", []) or []
            if ents:
                df = pd.DataFrame(ents)
                if 'redacted' in df.columns:
                    df['visibility'] = df['redacted'].map({True:'Protected', False:'Visible'})
                st.dataframe(df, use_container_width=True, height=320)
                st.caption(f"📊 {len(ents)} entities • Privacy & feedback applied")
            else:
                st.info("🔍 No entities detected.")

        # Tables
        with tabs[2]:
            st.markdown("#### 📊 Document Tables (Final)")
            tables = final_view.get("tables", []) or []
            if tables:
                for i,t in enumerate(tables):
                    with st.expander(f"Table {i+1}: {t.get('id','Unnamed')}", expanded=(i==0)):
                        rows = t.get("rows", []) or []
                        if rows:
                            try:
                                header, *data = rows if len(rows) > 1 else ([], rows)
                                if header and data and all(len(r) == len(header) for r in data):
                                    df = pd.DataFrame(data, columns=header)
                                else:
                                    df = pd.DataFrame(rows)
                                st.dataframe(df, use_container_width=True, height=240)
                            except Exception:
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, height=240)
                        else:
                            st.info("📝 Empty table.")
            else:
                st.info("📊 No tables detected.")

        # Raw OCR (Admin)
        if role == "admin" and len(tabs) > 3:
            with tabs[idx_raw]:
                st.markdown("#### Raw OCR Output")
                st.info("Admin view: Unfiltered OCR results")
                st.json(ocr)

        # Reinforcement (form + user-centric result)
        with tabs[idx_reinf]:
            st.markdown("#### Reinforcement: Human Feedback & Final Output")

            if not st.session_state.gov_result:
                st.info("Run the pipeline first to enable reinforcement.")
            else:
                with st.form("reinforcement_form", clear_on_submit=False):
                    apply_flag = st.checkbox("Apply reinforcement", value=True, help="Use Gemini to apply your feedback safely.")
                    placeholder_hint = "e.g., Standardize dates to YYYY-MM-DD, normalize currency to INR, fix mislabeled columns."
                    feedback_text = st.text_area("📝 Your Feedback", height=120, placeholder=placeholder_hint)
                    submitted = st.form_submit_button("Apply Feedback")

                if submitted:
                    set_agent("Reinf", status="Running", pct=85, tone="warn", step="Optimizing outputs")
                    # save a snapshot for comparison
                    st.session_state.pre_reinf_view = st.session_state.final_view
                    try:
                        with httpx.Client(timeout=90) as cli:
                            reinf = cli.post(f"{REINF_URL}/a2a/reinforce", json={
                                "protocol":"a2a.v1","intent":"doc.reinforce","job_id":st.session_state.job_id or f"job-{int(time.time())}",
                                "input":{
                                    "apply": bool(apply_flag),
                                    "feedback": feedback_text or "",
                                    "governance_result": st.session_state.gov_result,
                                    "viewer": {"role": role},
                                    "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
                                    "lawful_basis": "contract",
                                    "retention_days": 365
                                }
                            }, timeout=90.0).json()
                        st.session_state.reinf_result = reinf

                        r_status = reinf.get("status")
                        r_audit  = reinf.get("audit") or {}
                        r_reason = r_audit.get("reason")

                        if r_status == "ok":
                            # Update final view to model-merged output
                            st.session_state.final_view = reinf.get("final") or st.session_state.final_view
                            set_agent("Reinf", status="Complete", pct=100, tone="ok",
                                      step="Applied" if r_audit.get("applied_feedback") else "No changes")
                            st.success("Reinforcement applied." if r_audit.get("applied_feedback") else "No changes were necessary.")
                            st.rerun()
                        elif r_status == "skipped":
                            set_agent("Reinf", status="Skipped", pct=90, tone="warn",
                                      step=f"Skipped: {r_reason or 'see audit'}")
                            st.info(f"Reinforcement skipped. Reason: {r_reason or 'apply=false or policy/LLM constraint.'}")
                        else:
                            msg = r_reason or (reinf.get("detail") or "Unknown error")
                            set_agent("Reinf", status="Error", pct=90, tone="bad", step=f"Error: {msg}")
                            st.error(msg)
                    except Exception as e:
                        set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent call failed")
                        st.exception(e)

            # User-centric view of the latest reinforcement outcome
            reinf = st.session_state.reinf_result or {}
            if reinf:
                st.markdown("### Result overview")
                ra = reinf.get("audit") or {}
                applied = bool(ra.get("applied_feedback"))
                cols = st.columns(3)
                cols[0].markdown(f'<div class=\"su-glass stat\"><div>Status</div><div class="metric">{"Applied" if applied else reinf.get("status","n/a").title()}</div></div>', unsafe_allow_html=True)
                cols[1].markdown(f'<div class=\"su-glass stat\"><div>Latency (ms)</div><div class="metric">{(ra.get("latency_ms_total") or 0):,}</div></div>', unsafe_allow_html=True)
                cols[2].markdown(f'<div class=\"su-glass stat\"><div>Time</div><div class="metric">{ra.get("timestamp") or "—"}</div></div>', unsafe_allow_html=True)
                if ra.get("reason"):
                    st.markdown(f"<span class='su-chip'>Reason</span> {ra['reason']}", unsafe_allow_html=True)

                # Compare before/after for user-friendly summary
                before = st.session_state.pre_reinf_view or st.session_state.final_view
                after  = st.session_state.final_view
                if before and after and before is not after:
                    def count_words(x):
                        return len((x or {}).get("full_text"," ").split())
                    def count_ents(x):
                        return len((x or {}).get("entities") or [])
                    def count_tabs(x):
                        return len((x or {}).get("tables") or [])
                    w0,w1 = count_words(before), count_words(after)
                    e0,e1 = count_ents(before), count_ents(after)
                    t0,t1 = count_tabs(before), count_tabs(after)
                    dcol1,dcol2,dcol3 = st.columns(3)
                    def card(lbl,a,b,icon):
                        delta = b-a
                        arrow = "▲" if delta>0 else ("▼" if delta<0 else "→")
                        tone = "ok" if delta>0 else ("warn" if delta<0 else "")
                        dcol = {
                            dcol1: (lbl=="Words"),
                            dcol2: (lbl=="Entities"),
                            dcol3: (lbl=="Tables")
                        }
                        # choose target column by lbl
                        col = dcol1 if lbl=="Words" else dcol2 if lbl=="Entities" else dcol3
                        col.markdown(
                            f"<div class='su-glass stat'>{icon}<div>{lbl}</div><div class='metric'>{b:,} <span style='font-size:.9rem;opacity:.9'>({arrow} {abs(delta):,})</span></div></div>",
                            unsafe_allow_html=True
                        )
                    card("Words", w0, w1, "📝")
                    card("Entities", e0, e1, "🏷️")
                    card("Tables", t0, t1, "📊")

                    # Diff sample (text only)
                    text_before = (before or {}).get("full_text") or ""
                    text_after  = (after  or {}).get("full_text") or ""
                    diff_lines = list(difflib.unified_diff(
                        text_before.splitlines(), text_after.splitlines(), lineterm="", n=3
                    ))
                    if diff_lines:
                        with st.expander("See what changed (text diff)"):
                            st.code("\n".join(diff_lines), language="diff")
                
                st.markdown("### 📦 Final output")
                fcol1, fcol2 = st.columns([0.6,0.4])
                with fcol1:
                    st.text_area("Final text (copy friendly)", value=(st.session_state.final_view.get("full_text") or ""), height=220)
                    st.download_button(
                        "Download Final Text",
                        data=(st.session_state.final_view.get("full_text") or "").encode("utf-8"),
                        file_name=f"{st.session_state.job_id or 'job'}-final.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with fcol2:
                    ents = (st.session_state.final_view or {}).get("entities") or []
                    tables = (st.session_state.final_view or {}).get("tables") or []
                    st.markdown(f"<div class='su-glass stat'><div>Entities</div><div class='metric'>{len(ents)}</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='su-glass stat'><div>Tables</div><div class='metric'>{len(tables)}</div></div>", unsafe_allow_html=True)
                    st.download_button(
                        "⬇️ Download Final JSON",
                        data=json.dumps(st.session_state.final_view, indent=2).encode("utf-8"),
                        file_name=f"{st.session_state.job_id or 'job'}-final.json",
                        mime="application/json",
                        use_container_width=True
                    )

                with st.expander("🧑‍💻 View structured JSON (advanced)"):
                    st.json(st.session_state.final_view)

        # Audit tab
        with tabs[idx_audit]:
            st.markdown("#### 📋 Compliance Audit Trail")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Governance Audit**")
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
                st.markdown("**Reinforcement Audit**")
                reinf_audit = (st.session_state.reinf_result or {}).get("audit") if st.session_state.reinf_result else None
                if reinf_audit:
                    st.json(reinf_audit)
                else:
                    st.info("No reinforcement audit yet.")
            if redacts:
                st.markdown("**Redaction Details**")
                df_r = pd.DataFrame(redacts)
                st.dataframe(df_r, use_container_width=True, height=240)

    # Closing panel
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        '<div class="su-glass" style="text-align:center;">'
        '🚀 <strong>SureSight AI</strong> • Futuristic, privacy-first document intelligence'
        '</div>',
        unsafe_allow_html=True
    )

# ===================== Router (JS hooks for intro buttons) =====================
st.components.v1.html("""
<script>
window.addEventListener('message', (e)=>{
  if(!e.data) return;
  if(e.data.type==='streamlit:setPhase'){
    const data = {"phase": e.data.phase};
    window.parent.postMessage({isStreamlitMessage:true, type:'SET_COMPONENT_VALUE', value: data}, '*');
  }
  if(e.data.type==='streamlit:refreshHealth'){
    location.reload();
  }
});
</script>
""", height=0)

# ===================== Phase Switch =====================
if st.session_state.phase == "intro":
    render_intro()
else:
    render_app()
