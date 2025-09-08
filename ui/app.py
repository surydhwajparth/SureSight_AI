# # import os, json, base64, httpx, time
# # from dotenv import load_dotenv
# # import streamlit as st
# # import pandas as pd

# # load_dotenv()

# # # Service endpoints
# # OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
# # GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
# # REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# # # -------------- Page config & styles --------------
# # st.set_page_config(page_title="Suresight AI • Agentic OCR", layout="wide", initial_sidebar_state="collapsed")

# # STYLES = """
# # <style>
# # /* Global layout */
# # .block-container {padding-top: 0.5rem; padding-bottom: 2rem; max-width: 1400px;}
# # .main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
# #               padding: 2rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 20px 20px;}
# # .header-content {display: flex; justify-content: space-between; align-items: center; color: white;}
# # .logo-section {text-align: center; opacity: 0.9;}
# # .logo-icon {font-size: 3rem; margin-bottom: 0.5rem;}
# # .logo-text {font-size: 0.9rem; font-weight: 500; letter-spacing: 1px;}

# # /* Cards and containers */
# # .su-card {border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; 
# #           background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
# # .su-glass-card {background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
# #                 border: 1px solid rgba(255,255,255,0.2); border-radius: 16px; padding: 20px;}
# # .su-metric-card {background: linear-gradient(145deg, #f8fafc, #e2e8f0); 
# #                  border-radius: 12px; padding: 1rem; text-align: center; margin: 0.5rem 0;}

# # /* Text areas and content */
# # .sanitized-output {background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; 
# #                    padding: 1.5rem; font-family: 'Courier New', monospace; line-height: 1.6;
# #                    white-space: pre-wrap; max-height: 400px; overflow-y: auto;}
# # .redacted-text {background: #fee2e2; color: #991b1b; padding: 2px 6px; 
# #                 border-radius: 4px; font-weight: 600;}
# # .highlight-stats {background: #dbeafe; color: #1e40af; padding: 8px 12px; 
# #                   border-radius: 8px; font-size: 0.9rem; margin: 1rem 0;}

# # /* Status indicators */
# # .su-chip {display: inline-block; padding: 6px 12px; border-radius: 999px; 
# #           background: #f1f5f9; font-size: 0.85rem; font-weight: 500;}
# # .su-ok {color: #059669; font-weight: 600;}
# # .su-bad {color: #dc2626; font-weight: 600;}
# # .su-warning {color: #d97706; font-weight: 600;}
# # .status-dot {width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px;}
# # .dot-green {background: #10b981;}
# # .dot-red {background: #ef4444;}

# # /* Enhanced tabs */
# # .stTabs [data-baseweb="tab-list"] {gap: 8px;}
# # .stTabs [data-baseweb="tab"] {padding: 12px 24px; border-radius: 8px 8px 0 0; 
# #                               background: #f1f5f9; border: none;}
# # .stTabs [aria-selected="true"] {background: #3b82f6; color: white;}

# # /* Animations */
# # @keyframes fadeIn {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);}}
# # .fade-in {animation: fadeIn 0.3s ease-out;}

# # /* Utilities */
# # .su-subtle {color: #64748b;}
# # .text-center {text-align: center;}
# # footer {visibility: hidden;}
# # .stSpinner > div > div {border-color: #3b82f6 transparent transparent transparent;}
# # </style>
# # """
# # st.markdown(STYLES, unsafe_allow_html=True)

# # # -------------- Enhanced Header with Logos --------------
# # st.markdown("""
# # <div class="main-header">
# #     <div class="header-content">
# #         <div class="logo-section">
# #             <img src="static/logo-left.png" alt="Vision AI" style="width: 60px; height: 60px; margin-bottom: 0.5rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
# #             <div class="logo-icon" style="display: none;">🔍</div>
# #             <div class="logo-text">VISION AI</div>
# #         </div>
# #         <div style="text-align: center; flex-grow: 1;">
# #             <img src="static/suresight-logo.png" alt="Suresight AI" style="height: 50px; margin-bottom: 1rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
# #             <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; display: none;">Suresight AI</h1>
# #             <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
# #                 Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • Governance-ready (HIPAA/GDPR)
# #             </p>
# #         </div>
# #         <div class="logo-section">
# #             <img src="static/logo-right.png" alt="Secure" style="width: 60px; height: 60px; margin-bottom: 0.5rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
# #             <div class="logo-icon" style="display: none;">🛡️</div>
# #             <div class="logo-text">SECURE</div>
# #         </div>
# #     </div>
# # </div>
# # """, unsafe_allow_html=True)

# # # -------------- Service Status Card --------------
# # status_col1, status_col2 = st.columns([0.7, 0.3])

# # with status_col2:
# #     if st.button("🔄 Refresh Status", use_container_width=True, type="secondary"):
# #         st.session_state["_ping"] = time.time()
# #         st.rerun()

# # with status_col1:
# #     # Quick health indicators
# #     statuses = {}
# #     try:
# #         with httpx.Client(timeout=5) as cli:
# #             statuses["OCR"]   = cli.get(f"{OCR_URL}/health").json()
# #             statuses["Gov"]   = cli.get(f"{GOV_URL}/health").json()
# #             statuses["Reinf"] = cli.get(f"{REINF_URL}/health").json()
# #     except Exception:
# #         statuses = {}

# #     st.markdown('<div class="su-card fade-in">', unsafe_allow_html=True)
# #     st.markdown("**🔧 Service Health**")
    
# #     cols = st.columns(3)
# #     services = [
# #         ("OCR Engine", "OCR", "🔤"),
# #         ("Governance", "Gov", "🛡️"), 
# #         ("Reinforcement", "Reinf", "🚀")
# #     ]
    
# #     for i, (label, key, icon) in enumerate(services):
# #         with cols[i]:
# #             ok = bool(statuses.get(key, {}).get("ok", False))
# #             status_html = f"""
# #             <div style="text-align: center; padding: 1rem;">
# #                 <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
# #                 <div style="font-weight: 600; margin-bottom: 0.5rem;">{label}</div>
# #                 <div>
# #                     <span class="status-dot {'dot-green' if ok else 'dot-red'}"></span>
# #                     <span class="{'su-ok' if ok else 'su-bad'}">{'Online' if ok else 'Offline'}</span>
# #                 </div>
# #             </div>
# #             """
# #             st.markdown(status_html, unsafe_allow_html=True)
    
# #     st.markdown('</div>', unsafe_allow_html=True)

# # st.markdown("<br/>", unsafe_allow_html=True)

# # # -------------- Enhanced Controls --------------
# # st.markdown('<div class="su-card fade-in">', unsafe_allow_html=True)
# # st.markdown("### ⚙️ Configuration")

# # c1, c2, c3, c4 = st.columns([0.4, 0.2, 0.2, 0.2])

# # with c1:
# #     uploaded = st.file_uploader(
# #         "📄 Upload Document", 
# #         type=["png","jpg","jpeg"],
# #         help="Upload an image (PNG/JPG) • PDF support coming next"
# #     )

# # with c2:
# #     role = st.selectbox(
# #         "👤 User Role", 
# #         ["admin", "client"], 
# #         index=1, 
# #         help="Admin sees raw OCR; Client sees sanitized view only"
# #     )

# # with c3:
# #     human_req = st.selectbox(
# #         "🎯 Task Type", 
# #         ["extract (default)", "translate", "summarize"], 
# #         index=0
# #     )

# # with c4:
# #     target_locale = st.selectbox(
# #         "🌍 Locale", 
# #         ["en-IN","hi-IN","en-US","fr-FR"], 
# #         index=0
# #     )

# # run_col, info_col = st.columns([0.25, 0.75])
# # with run_col:
# #     run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

# # with info_col:
# #     if uploaded:
# #         st.success(f"✅ Ready to process: {uploaded.name}")
# #     else:
# #         st.info("📋 Upload a document to begin processing")

# # st.markdown('</div>', unsafe_allow_html=True)

# # # -------------- Helper Functions --------------
# # def b64_for_uploaded(file):
# #     return base64.b64encode(file.read()).decode("utf-8")

# # def metrics_from(ocr: dict):
# #     words = len((ocr.get("full_text") or "").split())
# #     ents  = len(ocr.get("entities") or [])
# #     tabs  = len(ocr.get("tables") or [])
# #     conf  = float(ocr.get("confidence") or 0.0)
# #     cls   = ocr.get("doc_class","unknown")
# #     return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

# # def format_sanitized_text(text, redaction_count):
# #     """Enhanced text formatting with redaction highlighting"""
# #     if not text:
# #         return "No text content available."
    
# #     # Replace [REDACTED] with styled spans
# #     formatted = text.replace("[REDACTED]", '<span class="redacted-text">[REDACTED]</span>')
    
# #     stats_html = f"""
# #     <div class="highlight-stats">
# #         📊 <strong>Text Analysis:</strong> {len(text.split())} words • 
# #         🔒 <strong>Redactions:</strong> {redaction_count} items protected
# #     </div>
# #     """
    
# #     return stats_html + f'<div class="sanitized-output">{formatted}</div>'

# # # -------------- Main Processing --------------
# # if run:
# #     if not uploaded:
# #         st.error("⚠️ Please upload a PNG/JPG document first.")
# #         st.stop()

# #     if uploaded.type not in ("image/png","image/jpeg"):
# #         st.warning("📋 Currently supporting PNG/JPG only. PDF support coming next.")
# #         st.stop()

# #     job_id = f"job-{int(time.time())}"
# #     page_images_b64 = [b64_for_uploaded(uploaded)]

# #     # Processing with enhanced progress indicators
# #     progress_bar = st.progress(0)
# #     status_text = st.empty()
    
# #     status_text.text("🔤 Processing OCR...")
# #     progress_bar.progress(25)
    
# #     with httpx.Client(timeout=120) as cli:
# #         ocr = cli.post(f"{OCR_URL}/a2a/ocr", json={
# #             "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
# #             "input":{"page_images_b64": page_images_b64, "hints":{"locale":"en-IN"}}
# #         }, timeout=120.0).json()

# #     status_text.text("🛡️ Applying governance rules...")
# #     progress_bar.progress(75)
    
# #     with httpx.Client(timeout=60) as cli:
# #         gov = cli.post(f"{GOV_URL}/a2a/govern", json={
# #             "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
# #             "input":{
# #                 "ocr_result": ocr,
# #                 "viewer": {"role": role},
# #                 "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
# #                 "lawful_basis": "contract",
# #                 "retention_days": 365
# #             }
# #         }, timeout=60.0).json()

# #     progress_bar.progress(100)
# #     status_text.text("✅ Processing complete!")
# #     time.sleep(0.5)
# #     progress_bar.empty()
# #     status_text.empty()

# #     # -------------- Enhanced Metrics Dashboard --------------
# #     m = metrics_from(ocr)
# #     st.markdown('<div class="su-card fade-in" style="margin-top: 2rem;">', unsafe_allow_html=True)
# #     st.markdown("### 📊 Document Analysis")
    
# #     mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    
# #     with mcol1:
# #         st.markdown(f"""
# #         <div class="su-metric-card">
# #             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📄</div>
# #             <div style="font-weight: 600;">Document Type</div>
# #             <div class="su-chip" style="margin-top: 0.5rem;">{m['doc_class']}</div>
# #         </div>
# #         """, unsafe_allow_html=True)
    
# #     with mcol2:
# #         conf_color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
# #         st.markdown(f"""
# #         <div class="su-metric-card">
# #             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{conf_color}</div>
# #             <div style="font-weight: 600;">Confidence</div>
# #             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['confidence']:.2f}</div>
# #         </div>
# #         """, unsafe_allow_html=True)
    
# #     with mcol3:
# #         st.markdown(f"""
# #         <div class="su-metric-card">
# #             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📝</div>
# #             <div style="font-weight: 600;">Words</div>
# #             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['words']:,}</div>
# #         </div>
# #         """, unsafe_allow_html=True)
    
# #     with mcol4:
# #         st.markdown(f"""
# #         <div class="su-metric-card">
# #             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏷️</div>
# #             <div style="font-weight: 600;">Entities</div>
# #             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['entities']}</div>
# #         </div>
# #         """, unsafe_allow_html=True)
    
# #     with mcol5:
# #         st.markdown(f"""
# #         <div class="su-metric-card">
# #             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
# #             <div style="font-weight: 600;">Tables</div>
# #             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['tables']}</div>
# #         </div>
# #         """, unsafe_allow_html=True)
    
# #     st.markdown('</div>', unsafe_allow_html=True)

# #     # -------------- Enhanced Tabs --------------
# #     tab_labels = ["🔒 Sanitized View", "🏷️ Entities", "📊 Tables"]
# #     if role == "admin":
# #         tab_labels.extend(["🔍 Raw OCR", "📋 Audit"])
# #     else:
# #         tab_labels.append("📋 Audit")
    
# #     tabs = st.tabs(tab_labels)

# #     sanitized = (gov.get("views") or {}).get("sanitized", {})
# #     redacts = gov.get("redaction_manifest", [])
# #     audit = gov.get("audit", {})

# #     # Enhanced Sanitized View Tab
# #     with tabs[0]:
# #         st.markdown("#### 🔒 Privacy-Protected Content")
        
# #         # Governance summary
# #         col1, col2 = st.columns([0.7, 0.3])
# #         with col1:
# #             formatted_text = format_sanitized_text(sanitized.get("full_text", ""), len(redacts))
# #             st.markdown(formatted_text, unsafe_allow_html=True)
        
# #         with col2:
# #             st.markdown(f"""
# #             <div class="su-card">
# #                 <h4>🛡️ Governance Summary</h4>
# #                 <p><strong>Policy:</strong> {gov.get('policy_version', 'N/A')}</p>
# #                 <p><strong>Redactions:</strong> {len(redacts)} items</p>
# #                 <p><strong>User Role:</strong> <span class="su-chip">{role}</span></p>
# #                 <p><strong>Export Status:</strong> 
# #                    <span class="{'su-ok' if gov.get('export_state') == 'exported' else 'su-warning'}">
# #                    {gov.get('export_state', 'unknown')}
# #                    </span>
# #                 </p>
# #             </div>
# #             """, unsafe_allow_html=True)

# #     # Enhanced Entities Tab
# #     with tabs[1]:
# #         st.markdown("#### 🏷️ Extracted Entities")
# #         ents = sanitized.get("entities", [])
# #         if ents:
# #             # Add redaction status indicators
# #             df = pd.DataFrame(ents)
# #             if 'redacted' in df.columns:
# #                 df['🔒 Status'] = df['redacted'].map({True: '🔒 Protected', False: '👁️ Visible'})
# #             st.dataframe(df, use_container_width=True, height=300)
# #             st.caption(f"📊 Showing {len(ents)} entities • Privacy rules applied based on your role")
# #         else:
# #             st.info("🔍 No entities detected in this document.")

# #     # Enhanced Tables Tab  
# #     with tabs[2]:
# #         st.markdown("#### 📊 Document Tables")
# #         tables = sanitized.get("tables", [])
# #         if tables:
# #             for i, t in enumerate(tables):
# #                 with st.expander(f"📋 Table {i+1}: {t.get('id', 'Unnamed')}", expanded=True):
# #                     rows = t.get("rows", [])
# #                     if rows:
# #                         try:
# #                             header, *data = rows if len(rows) > 1 else ([], rows)
# #                             if header and data and all(len(r) == len(header) for r in data):
# #                                 df = pd.DataFrame(data, columns=header)
# #                             else:
# #                                 df = pd.DataFrame(rows)
# #                             st.dataframe(df, use_container_width=True, height=200)
# #                         except Exception:
# #                             st.dataframe(pd.DataFrame(rows), use_container_width=True, height=200)
# #                     else:
# #                         st.info("📝 Empty table structure detected.")
# #         else:
# #             st.info("📊 No tables detected in this document.")

# #     # Raw OCR Tab (Admin only)
# #     if role == "admin" and len(tabs) > 3:
# #         with tabs[3]:
# #             st.markdown("#### 🔍 Raw OCR Output")
# #             st.info("👨‍💼 Admin view: Unfiltered OCR results for debugging and analysis")
# #             st.json(ocr)

# #     # Enhanced Audit Tab
# #     with tabs[-1]:
# #         st.markdown("#### 📋 Compliance Audit Trail")
        
# #         if audit:
# #             col1, col2 = st.columns(2)
# #             with col1:
# #                 st.markdown("**🕒 Processing Details**")
# #                 st.json({
# #                     "timestamp": audit.get("timestamp"),
# #                     "viewer_role": audit.get("viewer_role"),
# #                     "jurisdiction": audit.get("jurisdiction"),
# #                     "confidence": audit.get("confidence")
# #                 })
            
# #             with col2:
# #                 st.markdown("**📊 Governance Metrics**")
# #                 st.json({
# #                     "lawful_basis": audit.get("lawful_basis"),
# #                     "retention_days": audit.get("retention_days"),
# #                     "counts": audit.get("counts")
# #                 })
            
# #             if redacts:
# #                 st.markdown("**🔒 Redaction Details**")
# #                 redact_df = pd.DataFrame(redacts)
# #                 st.dataframe(redact_df, use_container_width=True, height=200)
# #         else:
# #             st.warning("⚠️ No audit information available.")

# # # Enhanced Footer
# # st.markdown("<br/><br/>", unsafe_allow_html=True)
# # st.markdown("""
# # <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 12px; margin-top: 2rem;">
# #     <div style="color: #64748b; font-size: 0.9rem;">
# #         🚀 <strong>Suresight AI</strong> • Intelligent Document Processing with Privacy-First Design<br/>
# #         Upload your sample documents to experience AI-powered OCR with enterprise-grade governance
# #     </div>
# # </div>
# # """, unsafe_allow_html=True)


# ############################Original File content ended####################################

# # import os, json, base64, httpx, time
# # from dotenv import load_dotenv
# # import streamlit as st
# # import pandas as pd

# # load_dotenv()

# # # ===================== Service endpoints =====================
# # OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
# # GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
# # REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# # # ===================== Asset paths (two logos) =====================
# # LEFT_LOGO  = "static/logo-left.png"
# # RIGHT_LOGO = "static/logo-right.png"
# # BRAND_LOGO = "static/suresight-logo.png"

# # # ===================== Page config =====================
# # st.set_page_config(
# #     page_title="SureSight AI • Agentic OCR",
# #     layout="wide",
# #     initial_sidebar_state="expanded"
# # )

# # # ===================== Global Style (Futuristic / Glass) =====================
# # STYLES = """
# # <style>
# # :root{
# #   --bg:#0a0f1e; --panel:#0e1430; --glass:rgba(255,255,255,0.06);
# #   --edge:rgba(255,255,255,0.12); --text:#e6e9f5; --muted:#9aa4bf; --accent:#7dd3fc;
# #   --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --chip:#11183b; --chipb:#1c2553;
# # }
# # html, body, [data-testid="stAppViewContainer"] { background: radial-gradient(1200px 600px at 20% 0%, #0f1a3c 0%, #0a0f1e 45%, #070b18 100%) !important; }
# # .block-container {padding-top: 0.8rem; padding-bottom: 2rem; max-width: 1400px;}
# # * { color: var(--text); }
# # a { color: var(--accent); }
# # .su-surface { background: linear-gradient(160deg, var(--panel) 0%, #0c1233 100%);
# #               border: 1px solid var(--edge); border-radius: 18px; padding: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset;}
# # .su-glass { background: var(--glass); border: 1px solid var(--edge); border-radius: 18px; padding: 18px; backdrop-filter: blur(10px);}
# # .su-chip { display:inline-flex; align-items:center; gap:.5rem; padding:6px 12px; border-radius:999px; background:linear-gradient(160deg,var(--chip),var(--chipb)); border:1px solid var(--edge); font-size:.85rem; }
# # .su-dot {width:10px; height:10px; border-radius:50%;}
# # .ok {background: var(--ok);} .warn{background:var(--warn);} .bad{background:var(--bad);}
# # .su-header {
# #   border-radius: 22px; padding: 28px;
# #   background: conic-gradient(from 220deg at 10% 10%, #1f3b8a, #0ea5e9, #673ab7, #0ea5e9, #1f3b8a);
# #   -webkit-mask: linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0);
# #   mask: linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0);
# #   box-shadow: 0 20px 80px rgba(14, 165, 233, .25);
# # }
# # .su-head-inner {display:flex; align-items:center; justify-content:space-between;}
# # .brand {display:flex; align-items:center; gap:14px;}
# # .brand img {height:44px;}
# # .brand h1 {margin:0; font-weight:800; letter-spacing:.6px;}
# # .brand-sub {margin:0; opacity:0.92;}
# # .hero {text-align:center; padding:48px 24px;}
# # .hero h1 {font-size:2.6rem; margin-bottom:.25rem; font-weight:900;}
# # .hero p {color:#dbeafe; opacity:.95; margin-top:.25rem;}
# # .cta-row {display:flex; gap:12px; justify-content:center; margin-top:20px;}
# # .cta {background: #11183b; border:1px solid var(--edge); padding:10px 16px; border-radius:12px; cursor:pointer;}
# # .cta-primary {background:linear-gradient(160deg,#2563eb,#0ea5e9); border:none; }
# # footer {visibility:hidden;}
# # /* Sanitized text */
# # .sanitized-shell { border-radius:16px; overflow:hidden; border:1px solid var(--edge); }
# # .sanitized-bar { display:flex; gap:10px; align-items:center; padding:10px 12px; background:linear-gradient(160deg,#0b122e,#0f1844); border-bottom:1px solid var(--edge);}
# # .sanitized-body { background: #0a0f1e; padding:14px; max-height:420px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; line-height:1.55; }
# # .redacted { background: rgba(239,68,68,.15); border: 1px dashed rgba(239,68,68,.5); padding: 2px 6px; border-radius:6px; color:#fecaca; }
# # .kv {display:grid; grid-template-columns: 160px 1fr; gap:10px; }
# # .stat {text-align:center; background: var(--glass); border:1px solid var(--edge); border-radius:14px; padding:10px;}
# # .metric {font-size:1.15rem; font-weight:800;}
# # /* Sidebar agent panel */
# # .sidebar-title {font-weight:700; margin-bottom:.2rem;}
# # .agent-card {border:1px solid var(--edge); border-radius:14px; padding:12px; margin-bottom:12px; background:var(--glass);}
# # .agent-row {display:flex; align-items:center; justify-content:space-between;}
# # .agent-name {font-weight:600;}
# # .agent-step {color:var(--muted); font-size:.85rem;}
# # .progress-wrap {height:6px; background:#10193b; border-radius:999px; overflow:hidden; margin-top:8px;}
# # .progress-inner {height:100%; background:linear-gradient(90deg,#22d3ee,#60a5fa,#a78bfa); width:0%;}
# # /* Tabs */
# # .stTabs [data-baseweb="tab-list"] {gap: 8px;}
# # .stTabs [data-baseweb="tab"] {padding: 10px 18px; border-radius: 10px 10px 0 0; background: #0e1534; border: 1px solid var(--edge);}
# # .stTabs [aria-selected="true"] {background: linear-gradient(160deg,#1e293b,#0b122e); color: white; border-bottom-color: transparent;}
# # /* Buttons */
# # .stButton>button, .stDownloadButton>button { border-radius:12px; }
# # .stSpinner > div > div {border-color: #38bdf8 transparent transparent transparent;}
# # </style>
# # """
# # st.markdown(STYLES, unsafe_allow_html=True)

# # # ===================== App State =====================
# # if "phase" not in st.session_state:
# #     st.session_state.phase = "intro"  # intro -> app
# # if "agent_state" not in st.session_state:
# #     st.session_state.agent_state = {
# #         "OCR": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
# #         "Gov": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
# #         "Reinf": {"status":"Idle","pct":0,"tone":"warn","step":"Waiting to start"},
# #     }
# # if "last_health" not in st.session_state:
# #     st.session_state.last_health = {}

# # # ===================== Helpers =====================
# # def b64_for_uploaded(file):
# #     # Reset pointer in case Streamlit partially read the buffer
# #     file.seek(0)
# #     return base64.b64encode(file.read()).decode("utf-8")

# # def metrics_from(ocr: dict):
# #     words = len((ocr.get("full_text") or "").split())
# #     ents  = len(ocr.get("entities") or [])
# #     tabs  = len(ocr.get("tables") or [])
# #     conf  = float(ocr.get("confidence") or 0.0)
# #     cls   = ocr.get("doc_class","unknown")
# #     return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

# # def fmt_sanitized_html(text, redaction_count, policy_version, role):
# #     if not text:
# #         text = "No text content available."
# #     safe_html = (
# #         text.replace("&","&amp;")
# #             .replace("<","&lt;")
# #             .replace(">","&gt;")
# #             .replace("[REDACTED]", '<span class="redacted">[REDACTED]</span>')
# #     )
# #     toolbar = f"""
# #     <div class="sanitized-bar">
# #       <span class="su-chip"><span class="su-dot ok"></span> Sanitized View</span>
# #       <span class="su-chip">Role: <strong>{role}</strong></span>
# #       <span class="su-chip">Policy: {policy_version}</span>
# #       <span class="su-chip">Redactions: <strong>{redaction_count}</strong></span>
# #     </div>
# #     """
# #     body = f'<div class="sanitized-body">{safe_html}</div>'
# #     return f'<div class="sanitized-shell">{toolbar}{body}</div>'

# # def ping_health():
# #     try:
# #         with httpx.Client(timeout=5) as cli:
# #             return {
# #                 "OCR": cli.get(f"{OCR_URL}/health").json(),
# #                 "Gov": cli.get(f"{GOV_URL}/health").json(),
# #                 "Reinf": cli.get(f"{REINF_URL}/health").json(),
# #             }
# #     except Exception:
# #         return {}

# # def agent_panel():
# #     st.sidebar.markdown("### ⚙️ Agents")
# #     st.sidebar.caption("Live status while your document is processed.")

# #     for label, key, icon in [("OCR Engine","OCR","🔤"), ("Governance","Gov","🛡️"), ("Reinforcement","Reinf","🚀")]:
# #         state = st.session_state.agent_state.get(key, {})
# #         with st.sidebar.container(border=False):
# #             st.sidebar.markdown(f"""
# #             <div class="agent-card">
# #               <div class="agent-row">
# #                 <div class="agent-name">{icon} {label}</div>
# #                 <div class="su-chip"><span class="su-dot {'ok' if state.get('tone')=='ok' else 'warn' if state.get('tone')=='warn' else 'bad'}"></span>{state.get('status','')}</div>
# #               </div>
# #               <div class="agent-step">{state.get('step','')}</div>
# #               <div class="progress-wrap"><div class="progress-inner" style="width:{int(state.get('pct',0))}%;"></div></div>
# #             </div>
# #             """, unsafe_allow_html=True)

# #     # Health ping + quick chips
# #     st.sidebar.markdown("### 🌐 Services")
# #     if st.sidebar.button("Refresh health", use_container_width=True):
# #         st.session_state.last_health = ping_health()
# #     if not st.session_state.last_health:
# #         st.session_state.last_health = ping_health()

# #     cols = st.sidebar.columns(3)
# #     for i,(label,key) in enumerate([("OCR","OCR"),("Gov","Gov"),("Reinf","Reinf")]):
# #         ok = bool(st.session_state.last_health.get(key,{}).get("ok", False))
# #         cols[i].markdown(
# #             f'<span class="su-chip"><span class="su-dot {"ok" if ok else "bad"}"></span>{label}</span>',
# #             unsafe_allow_html=True
# #         )

# #     # Extra: show OCR PDF support if reported
# #     ocr_health = st.session_state.last_health.get("OCR") or {}
# #     if "pdf_support" in ocr_health:
# #         supported = "ok" if ocr_health.get("pdf_support") else "bad"
# #         st.sidebar.markdown(
# #             f'<span class="su-chip"><span class="su-dot {supported}"></span>PDF Support</span>',
# #             unsafe_allow_html=True
# #         )

# # def set_agent(key, status=None, pct=None, tone=None, step=None):
# #     cur = st.session_state.agent_state.get(key, {})
# #     if status is not None: cur["status"]=status
# #     if pct is not None: cur["pct"]=pct
# #     if tone is not None: cur["tone"]=tone
# #     if step is not None: cur["step"]=step
# #     st.session_state.agent_state[key]=cur

# # # ===================== Header (brand) =====================
# # def top_header():
# #     st.markdown("""
# #     <div class="su-header">
# #       <div class="su-head-inner">
# #         <div class="brand">
# #           <img src='""" + LEFT_LOGO + """' onerror="this.style.display='none';this.insertAdjacentText('afterend','🔍');"/>
# #           <h1>SureSight AI</h1>
# #         </div>
# #         <div class="brand">
# #           <p class="brand-sub">Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • HIPAA/GDPR Ready</p>
# #         </div>
# #         <div class="brand">
# #           <img src='""" + RIGHT_LOGO + """' onerror="this.style.display='none';this.insertAdjacentText('afterend','🛡️');"/>
# #         </div>
# #       </div>
# #     </div>
# #     """, unsafe_allow_html=True)

# # # ===================== Intro Screen =====================
# # def render_intro():
# #     top_header()
# #     st.markdown("""
# #     <div class="su-surface hero">
# #       <img src='""" + BRAND_LOGO + """' style="height:56px;opacity:.95;" onerror="this.style.display='none';">
# #       <h1>Welcome to SureSight AI</h1>
# #       <p>Futuristic, privacy-first document intelligence. Upload, govern, and trust your data—end to end.</p>
# #       <div class="cta-row">
# #         <button class="cta cta-primary" onclick="window.parent.postMessage({type:'streamlit:setPhase', phase:'app'}, '*')">Get Started</button>
# #         <button class="cta" onclick="window.parent.postMessage({type:'streamlit:refreshHealth'}, '*')">Check Services</button>
# #       </div>
# #     </div>
# #     """, unsafe_allow_html=True)

# #     # Fallback for JS-less navigation
# #     st.write("")
# #     c1, c2 = st.columns([0.3,0.7])
# #     with c1:
# #         if st.button("🚀 Enter Workspace", use_container_width=True):
# #             st.session_state.phase = "app"
# #             st.rerun()
# #     with c2:
# #         if st.button("🔄 Refresh Health", use_container_width=True):
# #             st.session_state.last_health = ping_health()
# #             st.success("Health refreshed")

# #     # Lightweight highlights / value props
# #     c1,c2,c3 = st.columns(3)
# #     with c1:
# #         st.markdown('<div class="su-glass stat"><div>🔒 Compliance-first</div><div class="metric">GDPR / HIPAA</div></div>', unsafe_allow_html=True)
# #     with c2:
# #         st.markdown('<div class="su-glass stat"><div>⚡ Agentic Workflow</div><div class="metric">OCR → Govern → Reinforce</div></div>', unsafe_allow_html=True)
# #     with c3:
# #         st.markdown('<div class="su-glass stat"><div>🧠 Multimodal</div><div class="metric">Gemini 2.5 Flash</div></div>', unsafe_allow_html=True)

# # # ===================== Main App (Workspace) =====================
# # def render_app():
# #     top_header()
# #     agent_panel()

# #     st.markdown("#### 🧪 Workspace")
# #     with st.container():
# #         c1,c2,c3,c4 = st.columns([0.42,0.19,0.19,0.20])
# #         with c1:
# #             uploaded = st.file_uploader(
# #                 "📄 Upload Document (PDF / PNG / JPG)",
# #                 type=["pdf","png","jpg","jpeg"],
# #                 help="You can upload a single PDF or image. PDFs are sent directly to the OCR service."
# #             )
# #         with c2:
# #             role = st.selectbox("👤 User Role", ["admin","client"], index=1, help="Admin: raw OCR; Client: sanitized")
# #         with c3:
# #             human_req = st.selectbox("🎯 Task Type", ["extract (default)","translate","summarize"], index=0)
# #         with c4:
# #             target_locale = st.selectbox("🌍 Locale", ["en-IN","hi-IN","en-US","fr-FR"], index=0)

# #     # Action row
# #     run_col, info_col = st.columns([0.25, 0.75])
# #     with run_col:
# #         run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)
# #     with info_col:
# #         if uploaded: st.success(f"✅ Ready to process: {uploaded.name}")
# #         else: st.info("📋 Upload a PDF or image to begin processing")

# #     # Quick service chips
# #     hc = st.columns(3)
# #     health = ping_health()
# #     for i,(label,key) in enumerate([("OCR","OCR"),("Governance","Gov"),("Reinforcement","Reinf")]):
# #         ok = bool(health.get(key,{}).get("ok", False))
# #         tone = "ok" if ok else "bad"
# #         hc[i].markdown(f'<span class="su-chip"><span class="su-dot {tone}"></span>{label}: {"Online" if ok else "Offline"}</span>', unsafe_allow_html=True)

# #     # ========== Processing ==========
# #     if run:
# #         if not uploaded:
# #             st.error("⚠️ Please upload a PDF/PNG/JPG document first.")
# #             st.stop()

# #         # Initialize agent panel progress
# #         for k in ["OCR","Gov","Reinf"]:
# #             set_agent(k, status="Queued", pct=0, tone="warn", step="Queued")

# #         job_id = f"job-{int(time.time())}"

# #         # Build OCR input payload depending on file type
# #         mime = uploaded.type or ""
# #         payload_input = {"hints": {"locale": target_locale, "task": human_req}}

# #         if mime == "application/pdf" or uploaded.name.lower().endswith(".pdf"):
# #             # Send as PDFs (base64) for direct ingestion by OCR service
# #             pdf_b64 = b64_for_uploaded(uploaded)
# #             payload_input["pdfs_b64"] = [pdf_b64]
# #             display_name = f"{uploaded.name} (PDF)"
# #         elif mime in ("image/png","image/jpeg") or uploaded.name.lower().endswith((".png",".jpg",".jpeg")):
# #             img_b64 = b64_for_uploaded(uploaded)
# #             payload_input["page_images_b64"] = [img_b64]
# #             display_name = f"{uploaded.name} (Image)"
# #         else:
# #             st.warning("📋 Unsupported file type. Please upload PDF, PNG, or JPG.")
# #             st.stop()

# #         # Progress UI
# #         progress_bar = st.progress(0)
# #         status_text = st.empty()

# #         # ---- OCR ----
# #         set_agent("OCR", status="Running", pct=20, tone="warn", step=f"Reading {display_name}")
# #         status_text.text("🔤 Processing OCR…")
# #         progress_bar.progress(20)
# #         try:
# #             with httpx.Client(timeout=180) as cli:
# #                 ocr = cli.post(f"{OCR_URL}/a2a/ocr", json={
# #                     "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
# #                     "input": payload_input
# #                 }, timeout=180.0).json()
# #         except Exception as e:
# #             set_agent("OCR", status="Error", pct=0, tone="bad", step="Failed to call OCR")
# #             st.exception(e)
# #             st.stop()

# #         set_agent("OCR", status="Complete", pct=40, tone="ok", step="Text extracted")

# #         # ---- Governance ----
# #         set_agent("Gov", status="Running", pct=50, tone="warn", step="Applying rules")
# #         status_text.text("🛡️ Applying governance rules…")
# #         progress_bar.progress(60)
# #         try:
# #             with httpx.Client(timeout=60) as cli:
# #                 gov = cli.post(f"{GOV_URL}/a2a/govern", json={
# #                     "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
# #                     "input":{
# #                         "ocr_result": ocr,
# #                         "viewer": {"role": role},
# #                         "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
# #                         "lawful_basis": "contract",
# #                         "retention_days": 365
# #                     }
# #                 }, timeout=60.0).json()
# #         except Exception as e:
# #             set_agent("Gov", status="Error", pct=60, tone="bad", step="Governance error")
# #             st.exception(e)
# #             st.stop()

# #         set_agent("Gov", status="Complete", pct=80, tone="ok", step="Sanitized view generated")

# #         # ---- Reinforcement (placeholder wiring preserved) ----
# #         set_agent("Reinf", status="Running", pct=85, tone="warn", step="Optimizing outputs")
# #         time.sleep(0.3)  # simulate a small step
# #         set_agent("Reinf", status="Complete", pct=100, tone="ok", step="Finalized")

# #         progress_bar.progress(100)
# #         status_text.text("✅ Processing complete!")
# #         time.sleep(0.4)
# #         progress_bar.empty(); status_text.empty()

# #         # ========== Analysis Cards ==========
# #         m = metrics_from(ocr)
# #         st.markdown("### 📊 Document Analysis")
# #         mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
# #         with mcol1:
# #             st.markdown(f'<div class="su-glass stat">📄<div>Document Type</div><div class="metric">{m["doc_class"]}</div></div>', unsafe_allow_html=True)
# #         with mcol2:
# #             color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
# #             st.markdown(f'<div class="su-glass stat">{color}<div>Confidence</div><div class="metric">{m["confidence"]:.2f}</div></div>', unsafe_allow_html=True)
# #         with mcol3:
# #             st.markdown(f'<div class="su-glass stat">📝<div>Words</div><div class="metric">{m["words"]:,}</div></div>', unsafe_allow_html=True)
# #         with mcol4:
# #             st.markdown(f'<div class="su-glass stat">🏷️<div>Entities</div><div class="metric">{m["entities"]}</div></div>', unsafe_allow_html=True)
# #         with mcol5:
# #             st.markdown(f'<div class="su-glass stat">📊<div>Tables</div><div class="metric">{m["tables"]}</div></div>', unsafe_allow_html=True)

# #         # ========== Tabs ==========
# #         tab_labels = ["🔒 Sanitized View", "🏷️ Entities", "📊 Tables"]
# #         if role == "admin":
# #             tab_labels.extend(["🔍 Raw OCR", "📋 Audit"])
# #         else:
# #             tab_labels.append("📋 Audit")
# #         tabs = st.tabs(tab_labels)

# #         sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
# #         redacts = gov.get("redaction_manifest", []) or []
# #         audit = gov.get("audit", {}) or {}

# #         # ---- Sanitized View ----
# #         with tabs[0]:
# #             st.markdown("#### 🔒 Privacy-Protected Content")
# #             colA, colB = st.columns([0.68, 0.32])

# #             with colA:
# #                 html = fmt_sanitized_html(
# #                     sanitized.get("full_text",""),
# #                     len(redacts),
# #                     gov.get("policy_version","N/A"),
# #                     role
# #                 )
# #                 st.markdown(html, unsafe_allow_html=True)

# #                 st.download_button(
# #                     "⬇️ Download Sanitized Text",
# #                     data=(sanitized.get("full_text") or "").encode("utf-8"),
# #                     file_name=f"{job_id}-sanitized.txt",
# #                     mime="text/plain",
# #                     use_container_width=True
# #                 )

# #             with colB:
# #                 st.markdown('<div class="su-surface">', unsafe_allow_html=True)
# #                 st.markdown("**🛡️ Governance Summary**")
# #                 kv = {
# #                     "Policy Version": gov.get('policy_version', 'N/A'),
# #                     "Redactions": len(redacts),
# #                     "User Role": role,
# #                     "Export State": gov.get('export_state', 'unknown'),
# #                     "Lawful Basis": (audit.get("lawful_basis") or "contract"),
# #                     "Retention (days)": (audit.get("retention_days") or 365)
# #                 }
# #                 st.json(kv)
# #                 if redacts:
# #                     with st.expander("🔍 Redaction Details", expanded=False):
# #                         df_r = pd.DataFrame(redacts)
# #                         st.dataframe(df_r, use_container_width=True, height=220)
# #                 st.markdown('</div>', unsafe_allow_html=True)

# #         # ---- Entities ----
# #         with tabs[1]:
# #             st.markdown("#### 🏷️ Extracted Entities")
# #             ents = sanitized.get("entities", []) or []
# #             if ents:
# #                 df = pd.DataFrame(ents)
# #                 if 'redacted' in df.columns:
# #                     df['visibility'] = df['redacted'].map({True:'🔒 Protected', False:'👁️ Visible'})
# #                 st.dataframe(df, use_container_width=True, height=300)
# #                 st.caption(f"📊 {len(ents)} entities • Visibility reflects your role")
# #             else:
# #                 st.info("🔍 No entities detected.")

# #         # ---- Tables ----
# #         with tabs[2]:
# #             st.markdown("#### 📊 Document Tables")
# #             tables = sanitized.get("tables", []) or []
# #             if tables:
# #                 for i,t in enumerate(tables):
# #                     with st.expander(f"📋 Table {i+1}: {t.get('id','Unnamed')}", expanded=(i==0)):
# #                         rows = t.get("rows", []) or []
# #                         if rows:
# #                             try:
# #                                 header, *data = rows if len(rows) > 1 else ([], rows)
# #                                 if header and data and all(len(r) == len(header) for r in data):
# #                                     df = pd.DataFrame(data, columns=header)
# #                                 else:
# #                                     df = pd.DataFrame(rows)
# #                                 st.dataframe(df, use_container_width=True, height=220)
# #                             except Exception:
# #                                 st.dataframe(pd.DataFrame(rows), use_container_width=True, height=220)
# #                         else:
# #                             st.info("📝 Empty table structure detected.")
# #             else:
# #                 st.info("📊 No tables detected.")

# #         # ---- Raw OCR (Admin only) ----
# #         if role == "admin" and len(tabs) > 3:
# #             with tabs[3]:
# #                 st.markdown("#### 🔍 Raw OCR Output")
# #                 st.info("👨‍💼 Admin view: Unfiltered OCR results")
# #                 st.json(ocr)

# #         # ---- Audit ----
# #         with tabs[-1]:
# #             st.markdown("#### 📋 Compliance Audit Trail")
# #             if audit:
# #                 col1, col2 = st.columns(2)
# #                 with col1:
# #                     st.markdown("**🕒 Processing Details**")
# #                     st.json({
# #                         "timestamp": audit.get("timestamp"),
# #                         "viewer_role": audit.get("viewer_role"),
# #                         "jurisdiction": audit.get("jurisdiction"),
# #                         "confidence": audit.get("confidence")
# #                     })
# #                 with col2:
# #                     st.markdown("**📊 Governance Metrics**")
# #                     st.json({
# #                         "lawful_basis": audit.get("lawful_basis"),
# #                         "retention_days": audit.get("retention_days"),
# #                         "counts": audit.get("counts")
# #                     })
# #             else:
# #                 st.warning("⚠️ No audit information available.")

# #     # Closing panel
# #     st.markdown("<br/>", unsafe_allow_html=True)
# #     st.markdown(
# #         '<div class="su-glass" style="text-align:center;">'
# #         '🚀 <strong>SureSight AI</strong> • Futuristic, privacy-first document intelligence'
# #         '</div>',
# #         unsafe_allow_html=True
# #     )

# # # ===================== Router =====================
# # st.components.v1.html("""
# # <script>
# # window.addEventListener('message', (e)=>{
# #   if(!e.data) return;
# #   if(e.data.type==='streamlit:setPhase'){
# #     const data = {"phase": e.data.phase};
# #     window.parent.postMessage({isStreamlitMessage:true, type:'SET_COMPONENT_VALUE', value: data}, '*');
# #   }
# #   if(e.data.type==='streamlit:refreshHealth'){
# #     location.reload();
# #   }
# # });
# # </script>
# # """, height=0)

# # if st.session_state.phase == "intro":
# #     render_intro()
# # else:
# #     render_app()



# ################################with reinforcement##########################################
# import os, json, base64, httpx, time
# from dotenv import load_dotenv
# import streamlit as st
# import pandas as pd

# load_dotenv()

# # Service endpoints
# OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
# GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
# REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# # -------------- Page config & styles --------------
# st.set_page_config(page_title="Suresight AI • Agentic OCR", layout="wide", initial_sidebar_state="collapsed")

# STYLES = """
# <style>
# /* Global layout */
# .block-container {padding-top: 0.5rem; padding-bottom: 2rem; max-width: 1400px;}
# .main-header {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
#               padding: 2rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 20px 20px;}
# .header-content {display: flex; justify-content: space-between; align-items: center; color: white;}
# .logo-section {text-align: center; opacity: 0.9;}
# .logo-icon {font-size: 3rem; margin-bottom: 0.5rem;}
# .logo-text {font-size: 0.9rem; font-weight: 500; letter-spacing: 1px;}

# /* Cards and containers */
# .su-card {border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; 
#           background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
# .su-glass-card {background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
#                 border: 1px solid rgba(255,255,255,0.2); border-radius: 16px; padding: 20px;}
# .su-metric-card {background: linear-gradient(145deg, #f8fafc, #e2e8f0); 
#                  border-radius: 12px; padding: 1rem; text-align: center; margin: 0.5rem 0;}

# /* Text areas and content */
# .sanitized-output {background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 12px; 
#                    padding: 1.5rem; font-family: 'Courier New', monospace; line-height: 1.6;
#                    white-space: pre-wrap; max-height: 400px; overflow-y: auto;}
# .redacted-text {background: #fee2e2; color: #991b1b; padding: 2px 6px; 
#                 border-radius: 4px; font-weight: 600;}
# .highlight-stats {background: #dbeafe; color: #1e40af; padding: 8px 12px; 
#                   border-radius: 8px; font-size: 0.9rem; margin: 1rem 0;}

# /* Status indicators */
# .su-chip {display: inline-block; padding: 6px 12px; border-radius: 999px; 
#           background: #f1f5f9; font-size: 0.85rem; font-weight: 500;}
# .su-ok {color: #059669; font-weight: 600;}
# .su-bad {color: #dc2626; font-weight: 600;}
# .su-warning {color: #d97706; font-weight: 600;}
# .status-dot {width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 8px;}
# .dot-green {background: #10b981;}
# .dot-red {background: #ef4444;}

# /* Enhanced tabs */
# .stTabs [data-baseweb="tab-list"] {gap: 8px;}
# .stTabs [data-baseweb="tab"] {padding: 12px 24px; border-radius: 8px 8px 0 0; 
#                               background: #f1f5f9; border: none;}
# .stTabs [aria-selected="true"] {background: #3b82f6; color: white;}

# /* Animations */
# @keyframes fadeIn {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);}}
# .fade-in {animation: fadeIn 0.3s ease-out;}

# /* Utilities */
# .su-subtle {color: #64748b;}
# .text-center {text-align: center;}
# footer {visibility: hidden;}
# .stSpinner > div > div {border-color: #3b82f6 transparent transparent transparent;}
# </style>
# """
# st.markdown(STYLES, unsafe_allow_html=True)

# # -------------- Enhanced Header with Logos --------------
# st.markdown("""
# <div class="main-header">
#     <div class="header-content">
#         <div class="logo-section">
#             <img src="static/logo-left.png" alt="Vision AI" style="width: 60px; height: 60px; margin-bottom: 0.5rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
#             <div class="logo-icon" style="display: none;">🔍</div>
#             <div class="logo-text">VISION AI</div>
#         </div>
#         <div style="text-align: center; flex-grow: 1;">
#             <img src="static/suresight-logo.png" alt="Suresight AI" style="height: 50px; margin-bottom: 1rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
#             <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; display: none;">Suresight AI</h1>
#             <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
#                 Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • Governance-ready (HIPAA/GDPR)
#             </p>
#         </div>
#         <div class="logo-section">
#             <img src="static/logo-right.png" alt="Secure" style="width: 60px; height: 60px; margin-bottom: 0.5rem;" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
#             <div class="logo-icon" style="display: none;">🛡️</div>
#             <div class="logo-text">SECURE</div>
#         </div>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # -------------- Service Status Card --------------
# status_col1, status_col2 = st.columns([0.7, 0.3])

# with status_col2:
#     if st.button("🔄 Refresh Status", use_container_width=True, type="secondary"):
#         st.session_state["_ping"] = time.time()
#         st.rerun()

# with status_col1:
#     # Quick health indicators
#     statuses = {}
#     try:
#         with httpx.Client(timeout=5) as cli:
#             statuses["OCR"]   = cli.get(f"{OCR_URL}/health").json()
#             statuses["Gov"]   = cli.get(f"{GOV_URL}/health").json()
#             statuses["Reinf"] = cli.get(f"{REINF_URL}/health").json()
#     except Exception:
#         statuses = {}

#     st.markdown('<div class="su-card fade-in">', unsafe_allow_html=True)
#     st.markdown("**🔧 Service Health**")
    
#     cols = st.columns(3)
#     services = [
#         ("OCR Engine", "OCR", "🔤"),
#         ("Governance", "Gov", "🛡️"), 
#         ("Reinforcement", "Reinf", "🚀")
#     ]
    
#     for i, (label, key, icon) in enumerate(services):
#         with cols[i]:
#             ok = bool(statuses.get(key, {}).get("ok", False))
#             status_html = f"""
#             <div style="text-align: center; padding: 1rem;">
#                 <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
#                 <div style="font-weight: 600; margin-bottom: 0.5rem;">{label}</div>
#                 <div>
#                     <span class="status-dot {'dot-green' if ok else 'dot-red'}"></span>
#                     <span class="{'su-ok' if ok else 'su-bad'}">{'Online' if ok else 'Offline'}</span>
#                 </div>
#             </div>
#             """
#             st.markdown(status_html, unsafe_allow_html=True)
    
#     st.markdown('</div>', unsafe_allow_html=True)

# st.markdown("<br/>", unsafe_allow_html=True)

# # -------------- Enhanced Controls --------------
# st.markdown('<div class="su-card fade-in">', unsafe_allow_html=True)
# st.markdown("### ⚙️ Configuration")

# c1, c2, c3, c4 = st.columns([0.4, 0.2, 0.2, 0.2])

# with c1:
#     uploaded = st.file_uploader(
#         "📄 Upload Document", 
#         type=["png","jpg","jpeg"],
#         help="Upload an image (PNG/JPG) • PDF support coming next"
#     )

# with c2:
#     role = st.selectbox(
#         "👤 User Role", 
#         ["admin", "client"], 
#         index=1, 
#         help="Admin sees raw OCR; Client sees sanitized view only"
#     )

# with c3:
#     human_req = st.selectbox(
#         "🎯 Task Type", 
#         ["extract (default)", "translate", "summarize"], 
#         index=0
#     )

# with c4:
#     target_locale = st.selectbox(
#         "🌍 Locale", 
#         ["en-IN","hi-IN","en-US","fr-FR"], 
#         index=0
#     )

# # Reinforcement controls
# rc1, rc2 = st.columns([0.22, 0.78])
# with rc1:
#     apply_reinf = st.checkbox("🚀 Apply Reinforcement", value=True,
#                               help="Use human feedback to refine the governance-sanitized output (LLM-backed).")
# with rc2:
#     placeholder_hint = {
#         "extract (default)": "e.g., Standardize dates to YYYY-MM-DD, normalize currency to INR, fix mislabeled columns.",
#         "translate": f"Translate full_text and entities to {target_locale}. Keep tokens like [REDACTED] and token:* unchanged.",
#         "summarize": "Summarize the document in 5 bullets. Keep redactions intact."
#     }[human_req]
#     feedback_text = st.text_area("📝 Human Feedback (optional but recommended)", height=80,
#                                  placeholder=placeholder_hint)

# run_col, info_col = st.columns([0.25, 0.75])
# with run_col:
#     run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

# with info_col:
#     if uploaded:
#         st.success(f"✅ Ready to process: {uploaded.name}")
#     else:
#         st.info("📋 Upload a document to begin processing")

# st.markdown('</div>', unsafe_allow_html=True)

# # -------------- Helper Functions --------------
# def b64_for_uploaded(file):
#     return base64.b64encode(file.read()).decode("utf-8")

# def metrics_from(ocr: dict):
#     words = len((ocr.get("full_text") or "").split())
#     ents  = len(ocr.get("entities") or [])
#     tabs  = len(ocr.get("tables") or [])
#     conf  = float(ocr.get("confidence") or 0.0)
#     cls   = ocr.get("doc_class","unknown")
#     return dict(words=words, entities=ents, tables=tabs, confidence=conf, doc_class=cls)

# def format_sanitized_text(text, redaction_count):
#     """Enhanced text formatting with redaction highlighting"""
#     if not text:
#         return "No text content available."
#     formatted = text.replace("[REDACTED]", '<span class="redacted-text">[REDACTED]</span>')
#     stats_html = f"""
#     <div class="highlight-stats">
#         📊 <strong>Text Analysis:</strong> {len(text.split())} words • 
#         🔒 <strong>Redactions:</strong> {redaction_count} items protected
#     </div>
#     """
#     return stats_html + f'<div class="sanitized-output">{formatted}</div>'

# # -------------- Main Processing --------------
# if run:
#     if not uploaded:
#         st.error("⚠️ Please upload a PNG/JPG document first.")
#         st.stop()

#     if uploaded.type not in ("image/png","image/jpeg"):
#         st.warning("📋 Currently supporting PNG/JPG only. PDF support coming next.")
#         st.stop()

#     job_id = f"job-{int(time.time())}"
#     page_images_b64 = [b64_for_uploaded(uploaded)]

#     # Processing with enhanced progress indicators
#     progress_bar = st.progress(0)
#     status_text = st.empty()
    
#     status_text.text("🔤 Processing OCR...")
#     progress_bar.progress(25)
    
#     with httpx.Client(timeout=120) as cli:
#         ocr = cli.post(f"{OCR_URL}/a2a/ocr", json={
#             "protocol":"a2a.v1","intent":"doc.extract","job_id":job_id,
#             "input":{"page_images_b64": page_images_b64, "hints":{"locale":"en-IN"}}
#         }, timeout=120.0).json()

#     status_text.text("🛡️ Applying governance rules...")
#     progress_bar.progress(65)
    
#     with httpx.Client(timeout=60) as cli:
#         gov = cli.post(f"{GOV_URL}/a2a/govern", json={
#             "protocol":"a2a.v1","intent":"doc.govern","job_id":job_id,
#             "input":{
#                 "ocr_result": ocr,
#                 "viewer": {"role": role},
#                 "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#                 "lawful_basis": "contract",
#                 "retention_days": 365
#             }
#         }, timeout=60.0).json()

#     # Always call the reinforcement agent; it will 'skip' if apply=False
#     status_text.text("🚀 Applying reinforcement...")
#     progress_bar.progress(85)
#     reinf = {}
#     try:
#         with httpx.Client(timeout=90) as cli:
#             reinf = cli.post(f"{REINF_URL}/a2a/reinforce", json={
#                 "protocol":"a2a.v1","intent":"doc.reinforce","job_id":job_id,
#                 "input":{
#                     "apply": bool(apply_reinf),
#                     "feedback": feedback_text or "",
#                     "governance_result": gov,
#                     "viewer": {"role": role},
#                     "jurisdiction": {"gdpr": True, "hipaa": True, "region": "EU"},
#                     "lawful_basis": "contract",
#                     "retention_days": 365
#                 }
#             }, timeout=90.0).json()
#     except Exception as e:
#         reinf = {"status":"error","detail":str(e)}

#     progress_bar.progress(100)
#     status_text.text("✅ Processing complete!")
#     time.sleep(0.5)
#     progress_bar.empty()
#     status_text.empty()

#     # -------------- Enhanced Metrics Dashboard --------------
#     m = metrics_from(ocr)
#     st.markdown('<div class="su-card fade-in" style="margin-top: 2rem;">', unsafe_allow_html=True)
#     st.markdown("### 📊 Document Analysis")
    
#     mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    
#     with mcol1:
#         st.markdown(f"""
#         <div class="su-metric-card">
#             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📄</div>
#             <div style="font-weight: 600;">Document Type</div>
#             <div class="su-chip" style="margin-top: 0.5rem;">{m['doc_class']}</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with mcol2:
#         conf_color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
#         st.markdown(f"""
#         <div class="su-metric-card">
#             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{conf_color}</div>
#             <div style="font-weight: 600;">Confidence</div>
#             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['confidence']:.2f}</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with mcol3:
#         st.markdown(f"""
#         <div class="su-metric-card">
#             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📝</div>
#             <div style="font-weight: 600;">Words</div>
#             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['words']:,}</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with mcol4:
#         st.markdown(f"""
#         <div class="su-metric-card">
#             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏷️</div>
#             <div style="font-weight: 600;">Entities</div>
#             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['entities']}</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     with mcol5:
#         st.markdown(f"""
#         <div class="su-metric-card">
#             <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
#             <div style="font-weight: 600;">Tables</div>
#             <div style="font-size: 1.2rem; font-weight: 700; margin-top: 0.5rem;">{m['tables']}</div>
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown('</div>', unsafe_allow_html=True)

#     # -------------- Views & Tabs --------------
#     sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
#     redacts = gov.get("redaction_manifest", []) or []
#     gov_audit = gov.get("audit", {}) or {}

#     # Final view comes from Reinforcement if available, else falls back to sanitized
#     final_view = (reinf or {}).get("final") or sanitized
#     reinf_audit = (reinf or {}).get("audit", {}) or {}
#     reinf_status = (reinf or {}).get("status")

#     # Tab labels
#     if role == "admin":
#         tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🔍 Raw OCR", "🚀 Reinforcement", "📋 Audit"]
#         idx_raw, idx_reinf, idx_audit = 3, 4, 5
#     else:
#         tab_labels = ["🔒 Final View", "🏷️ Entities", "📊 Tables", "🚀 Reinforcement", "📋 Audit"]
#         idx_reinf, idx_audit = 3, 4

#     tabs = st.tabs(tab_labels)

#     # Final View Tab
#     with tabs[0]:
#         st.markdown("#### 🔒 Final View (post-reinforcement if applied)")
#         formatted_text = format_sanitized_text(final_view.get("full_text", ""), len(redacts))
#         st.markdown(formatted_text, unsafe_allow_html=True)

#         # Summary card
#         applied_badge = "✅ Applied" if reinf_status == "ok" and reinf_audit.get("applied_feedback", False) else "⏭️ Skipped"
#         col1, col2 = st.columns([0.7, 0.3])
#         with col2:
#             st.markdown(f"""
#             <div class="su-card">
#                 <h4>🧷 Summary</h4>
#                 <p><strong>Policy:</strong> {gov.get('policy_version', 'N/A')}</p>
#                 <p><strong>Redactions:</strong> {len(redacts)} items</p>
#                 <p><strong>Reinforcement:</strong> <span class="su-chip">{applied_badge}</span></p>
#                 <p><strong>User Role:</strong> <span class="su-chip">{role}</span></p>
#             </div>
#             """, unsafe_allow_html=True)

#     # Entities Tab (Final)
#     with tabs[1]:
#         st.markdown("#### 🏷️ Entities (Final)")
#         ents = final_view.get("entities", []) or []
#         if ents:
#             df = pd.DataFrame(ents)
#             if 'redacted' in df.columns:
#                 df['🔒 Status'] = df['redacted'].map({True: '🔒 Protected', False: '👁️ Visible'})
#             st.dataframe(df, use_container_width=True, height=300)
#             st.caption(f"📊 Showing {len(ents)} entities • Privacy & feedback applied")
#         else:
#             st.info("🔍 No entities detected in this document.")

#     # Tables Tab (Final)
#     with tabs[2]:
#         st.markdown("#### 📊 Document Tables (Final)")
#         tables = final_view.get("tables", []) or []
#         if tables:
#             for i, t in enumerate(tables):
#                 with st.expander(f"📋 Table {i+1}: {t.get('id', 'Unnamed')}", expanded=True):
#                     rows = t.get("rows", []) or []
#                     if rows:
#                         try:
#                             header, *data = rows if len(rows) > 1 else ([], rows)
#                             if header and data and all(len(r) == len(header) for r in data):
#                                 df = pd.DataFrame(data, columns=header)
#                             else:
#                                 df = pd.DataFrame(rows)
#                             st.dataframe(df, use_container_width=True, height=200)
#                         except Exception:
#                             st.dataframe(pd.DataFrame(rows), use_container_width=True, height=200)
#                     else:
#                         st.info("📝 Empty table structure detected.")
#         else:
#             st.info("📊 No tables detected in this document.")

#     # Raw OCR Tab (Admin only)
#     if role == "admin":
#         with tabs[idx_raw]:
#             st.markdown("#### 🔍 Raw OCR Output")
#             st.info("👨‍💼 Admin view: Unfiltered OCR results for debugging and analysis")
#             st.json(ocr)

#     # Reinforcement Tab
#     with tabs[idx_reinf]:
#         st.markdown("#### 🚀 Reinforcement")
#         if reinf_status in ("ok", "skipped"):
#             st.json({
#                 "status": reinf_status,
#                 "applied_feedback": reinf_audit.get("applied_feedback"),
#                 "model": reinf_audit.get("model"),
#                 "sdk": reinf_audit.get("sdk"),
#                 "latency_ms_total": reinf_audit.get("latency_ms_total"),
#                 "timestamp": reinf_audit.get("timestamp")
#             })
#             if feedback_text:
#                 st.markdown("**📝 Feedback Used**")
#                 st.code(feedback_text, language="markdown")
#             st.markdown("**📦 Final JSON**")
#             st.json(final_view)
#         else:
#             st.warning("Reinforcement agent response unavailable or errored.")
#             if isinstance(reinf, dict) and reinf.get("detail"):
#                 st.error(reinf.get("detail"))

#     # Audit Tab
#     with tabs[idx_audit]:
#         st.markdown("#### 📋 Compliance Audit Trail")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.markdown("**🕒 Governance Audit**")
#             if gov_audit:
#                 st.json({
#                     "timestamp": gov_audit.get("timestamp"),
#                     "viewer_role": gov_audit.get("viewer_role"),
#                     "jurisdiction": gov_audit.get("jurisdiction"),
#                     "confidence": gov_audit.get("confidence"),
#                     "lawful_basis": gov_audit.get("lawful_basis"),
#                     "retention_days": gov_audit.get("retention_days"),
#                     "counts": gov_audit.get("counts")
#                 })
#             else:
#                 st.info("No governance audit available.")
#         with col2:
#             st.markdown("**🚀 Reinforcement Audit**")
#             if reinf_audit:
#                 st.json(reinf_audit)
#             else:
#                 st.info("No reinforcement audit available.")
#         if redacts:
#             st.markdown("**🔒 Redaction Details**")
#             redact_df = pd.DataFrame(redacts)
#             st.dataframe(redact_df, use_container_width=True, height=200)

# # Enhanced Footer
# st.markdown("<br/><br/>", unsafe_allow_html=True)
# st.markdown("""
# <div style="text-align: center; padding: 2rem; background: #f8fafc; border-radius: 12px; margin-top: 2rem;">
#     <div style="color: #64748b; font-size: 0.9rem;">
#         🚀 <strong>Suresight AI</strong> • Intelligent Document Processing with Privacy-First Design<br/>
#         Upload your sample documents to experience AI-powered OCR with enterprise-grade governance
#     </div>
# </div>
# """, unsafe_allow_html=True)


# app.py
import os, json, base64, httpx, time
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

load_dotenv()

# ===================== Service endpoints =====================
OCR_URL   = f"http://localhost:{os.getenv('OCR_PORT','8081')}"
GOV_URL   = f"http://localhost:{os.getenv('GOV_PORT','8082')}"
REINF_URL = f"http://localhost:{os.getenv('REINF_PORT','8083')}"

# ===================== Asset paths (logos) =====================
LEFT_LOGO  = r"C:\Users\ParthSurydhwaj\Downloads\ADROSONIC LOGO BLACK.png"
RIGHT_LOGO = "static/logo-right.png"
BRAND_LOGO = "static/suresight-logo.png"

# ===================== Page config =====================
st.set_page_config(page_title="SureSight AI • Agentic OCR", layout="wide", initial_sidebar_state="expanded")

# ===================== Global Style (Futuristic / Glass) =====================
STYLES = """
<style>
:root{
  --bg:#0a0f1e; --panel:#0e1430; --glass:rgba(255,255,255,0.06);
  --edge:rgba(255,255,255,0.12); --text:#e6e9f5; --muted:#9aa4bf; --accent:#7dd3fc;
  --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444; --chip:#11183b; --chipb:#1c2553;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 20% 0%, #0f1a3c 0%, #0a0f1e 45%, #070b18 100%) !important;
}
.block-container {padding-top: .8rem; padding-bottom: 2rem; max-width: 1400px;}
* { color: var(--text); }
a { color: var(--accent); }
.su-surface { background: linear-gradient(160deg, var(--panel) 0%, #0c1233 100%);
              border: 1px solid var(--edge); border-radius: 18px; padding: 18px; box-shadow: 0 0 0 1px rgba(255,255,255,0.03) inset;}
.su-glass { background: var(--glass); border: 1px solid var(--edge); border-radius: 18px; padding: 18px; backdrop-filter: blur(10px);}
.su-chip { display:inline-flex; align-items:center; gap:.5rem; padding:6px 12px; border-radius:999px; background:linear-gradient(160deg,var(--chip),var(--chipb)); border:1px solid var(--edge); font-size:.85rem; }
.su-dot {width:10px; height:10px; border-radius:50%;}
.ok {background: var(--ok);} .warn{background:var(--warn);} .bad{background:var(--bad);}
.su-header {
  border-radius: 22px; padding: 28px;
  background: conic-gradient(from 220deg at 10% 10%, #1f3b8a, #0ea5e9, #673ab7, #0ea5e9, #1f3b8a);
  box-shadow: 0 20px 80px rgba(14, 165, 233, .25);
}
.su-head-inner {display:flex; align-items:center; justify-content:space-between;}
.brand {display:flex; align-items:center; gap:14px;}
.brand img {height:44px;}
.brand h1 {margin:0; font-weight:800; letter-spacing:.6px;}
.brand-sub {margin:0; opacity:0.92;}
.hero {text-align:center; padding:48px 24px;}
.hero h1 {font-size:2.6rem; margin-bottom:.25rem; font-weight:900;}
.hero p {color:#dbeafe; opacity:.95; margin-top:.25rem;}
.cta-row {display:flex; gap:12px; justify-content:center; margin-top:20px;}
.cta {background: #11183b; border:1px solid var(--edge); padding:10px 16px; border-radius:12px; cursor:pointer;}
.cta-primary {background:linear-gradient(160deg,#2563eb,#0ea5e9); border:none; }
footer {visibility:hidden;}
/* Sanitized text */
.sanitized-shell { border-radius:16px; overflow:hidden; border:1px solid var(--edge); }
.sanitized-bar { display:flex; gap:10px; align-items:center; padding:10px 12px; background:linear-gradient(160deg,#0b122e,#0f1844); border-bottom:1px solid var(--edge);}
.sanitized-body { background: #0a0f1e; padding:14px; max-height:420px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; line-height:1.55; }
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
.progress-wrap {height:6px; background:#10193b; border-radius:999px; overflow:hidden; margin-top:8px;}
.progress-inner {height:100%; background:linear-gradient(90deg,#22d3ee,#60a5fa,#a78bfa); width:0%;}
/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {padding: 10px 18px; border-radius: 10px 10px 0 0; background: #0e1534; border: 1px solid var(--edge);}
.stTabs [aria-selected="true"] {background: linear-gradient(160deg,#1e293b,#0b122e); color: white; border-bottom-color: transparent;}
/* Buttons */
.stButton>button, .stDownloadButton>button { border-radius:12px; }
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
for k in ["job_id","ocr_result","gov_result","reinf_result","final_view","role","redacts","gov_audit"]:
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
    safe_html = (
        text.replace("&","&amp;")
            .replace("<","&lt;")
            .replace(">","&gt;")
            .replace("[REDACTED]", '<span class="redacted">[REDACTED]</span>')
    )
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
    <div class="su-header">
      <div class="su-head-inner">
        <div class="brand">
          <img src='{LEFT_LOGO}' onerror="this.style.display='none';this.insertAdjacentText('afterend','🔍');"/>
          <h1>SureSight AI</h1>
        </div>
        <div class="brand">
          <p class="brand-sub">Agentic OCR • CrewAI + A2A • Gemini 2.5 Flash • HIPAA/GDPR Ready</p>
        </div>
        <div class="brand">
          <img src='{RIGHT_LOGO}' onerror="this.style.display='none';this.insertAdjacentText('afterend','🛡️');"/>
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
        if st.button("🚀 Enter Workspace", use_container_width=True):
            st.session_state.phase = "app"; st.rerun()
    with c2:
        if st.button("🔄 Refresh Health", use_container_width=True):
            st.session_state.last_health = ping_health()
            st.success("Health refreshed")

    # Mini highlights
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="su-glass stat"><div>🔒 Compliance-first</div><div class="metric">GDPR / HIPAA</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="su-glass stat"><div>⚡ Agentic Workflow</div><div class="metric">OCR → Govern → Reinforce</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="su-glass stat"><div>🧠 Multimodal</div><div class="metric">Gemini 2.5 Flash</div></div>', unsafe_allow_html=True)

# ===================== Main App (Workspace) =====================
def render_app():
    top_header()
    agent_panel()

    st.markdown("#### 🧪 Workspace")
    with st.container():
        c1,c2,c3,c4 = st.columns([0.42,0.19,0.19,0.20])
        with c1:
            uploaded = st.file_uploader(
                "📄 Upload Document (PNG / JPG)",
                type=["png","jpg","jpeg"],
                help="Upload an image (PNG/JPG)."
            )
        with c2:
            role = st.selectbox("👤 User Role", ["admin","client"], index=1, help="Admin: raw OCR; Client: sanitized")
        with c3:
            human_req = st.selectbox("🎯 Task Type", ["extract (default)","translate","summarize"], index=0)
        with c4:
            target_locale = st.selectbox("🌍 Locale", ["en-IN","hi-IN","en-US","fr-FR"], index=0)

    run_col, info_col = st.columns([0.25, 0.75])
    with run_col:
        run = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)
    with info_col:
        if uploaded: st.success(f"✅ Ready to process: {uploaded.name}")
        else: st.info("📋 Upload a PNG/JPG to begin processing")

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
        status_text.text("🔤 Processing OCR…")
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
        status_text.text("🛡️ Applying governance rules…")
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
        status_text.text("✅ OCR & Governance complete")

        # Save results in session
        st.session_state.ocr_result = ocr
        st.session_state.gov_result = gov
        st.session_state.reinf_result = None  # reset any previous reinforcement
        sanitized = (gov.get("views") or {}).get("sanitized", {}) or {}
        st.session_state.final_view = sanitized
        st.session_state.redacts = gov.get("redaction_manifest", []) or []
        st.session_state.gov_audit = gov.get("audit", {}) or {}

        # Finish progress
        set_agent("Reinf", status="Idle", pct=80, tone="warn", step="Awaiting feedback")
        progress_bar.progress(100); status_text.text("🧷 Provide reinforcement feedback in the Reinforcement tab.")
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
            st.markdown(f'<div class="su-glass stat">📄<div>Document Type</div><div class="metric">{m["doc_class"]}</div></div>', unsafe_allow_html=True)
        with mcol2:
            color = "🟢" if m['confidence'] > 0.8 else "🟡" if m['confidence'] > 0.6 else "🔴"
            st.markdown(f'<div class="su-glass stat">{color}<div>Confidence</div><div class="metric">{m["confidence"]:.2f}</div></div>', unsafe_allow_html=True)
        with mcol3:
            st.markdown(f'<div class="su-glass stat">📝<div>Words</div><div class="metric">{m["words"]:,}</div></div>', unsafe_allow_html=True)
        with mcol4:
            st.markdown(f'<div class="su-glass stat">🏷️<div>Entities</div><div class="metric">{m["entities"]}</div></div>', unsafe_allow_html=True)
        with mcol5:
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
            st.markdown("#### 🔒 Final View (post-reinforcement if applied)")
            html = fmt_sanitized_html(
                final_view.get("full_text",""),
                len(redacts),
                gov.get("policy_version","N/A"),
                role
            )
            st.markdown(html, unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Final Text",
                data=(final_view.get("full_text") or "").encode("utf-8"),
                file_name=f"{st.session_state.job_id or 'job'}-final.txt",
                mime="text/plain",
                use_container_width=True
            )

        # Entities
        with tabs[1]:
            st.markdown("#### 🏷️ Entities (Final)")
            ents = final_view.get("entities", []) or []
            if ents:
                df = pd.DataFrame(ents)
                if 'redacted' in df.columns:
                    df['visibility'] = df['redacted'].map({True:'🔒 Protected', False:'👁️ Visible'})
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
                    with st.expander(f"📋 Table {i+1}: {t.get('id','Unnamed')}", expanded=(i==0)):
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
                st.markdown("#### 🔍 Raw OCR Output")
                st.info("👨‍💼 Admin view: Unfiltered OCR results")
                st.json(ocr)

        # Reinforcement (separate tab: comment + final JSON)
        with tabs[idx_reinf]:
            st.markdown("#### 🚀 Reinforcement: Human Feedback & Final Output")
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
                        # Update final view if applied/ok
                        if reinf.get("status") == "ok":
                            st.session_state.final_view = reinf.get("final") or st.session_state.final_view
                            set_agent("Reinf", status="Complete", pct=100, tone="ok", step="Finalized")
                            st.success("Reinforcement applied.")
                            st.experimental_rerun()
                        elif reinf.get("status") == "skipped":
                            set_agent("Reinf", status="Skipped", pct=90, tone="warn", step="Skipped by user")
                            st.info("Reinforcement skipped. Showing sanitized output.")
                        else:
                            set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent error")
                            st.error(reinf.get("detail") or "Reinforcement error.")
                    except Exception as e:
                        set_agent("Reinf", status="Error", pct=90, tone="bad", step="Agent call failed")
                        st.exception(e)

            # Show last reinforcement audit/result (if any)
            reinf = st.session_state.reinf_result or {}
            if reinf:
                st.markdown("**Status & Audit**")
                st.json({
                    "status": reinf.get("status"),
                    "applied_feedback": (reinf.get("audit") or {}).get("applied_feedback"),
                    "model": (reinf.get("audit") or {}).get("model"),
                    "sdk": (reinf.get("audit") or {}).get("sdk"),
                    "latency_ms_total": (reinf.get("audit") or {}).get("latency_ms_total"),
                    "timestamp": (reinf.get("audit") or {}).get("timestamp")
                })
                st.markdown("**📦 Final JSON**")
                st.json(st.session_state.final_view)

        # Audit tab
        with tabs[idx_audit]:
            st.markdown("#### 📋 Compliance Audit Trail")
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
                reinf_audit = (st.session_state.reinf_result or {}).get("audit") if st.session_state.reinf_result else None
                if reinf_audit:
                    st.json(reinf_audit)
                else:
                    st.info("No reinforcement audit yet.")
            if redacts:
                st.markdown("**🔒 Redaction Details**")
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
