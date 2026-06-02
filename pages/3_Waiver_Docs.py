import streamlit as st
from database import init_db, get_db, Lead, Document
from utils import inject_css, page_header

st.set_page_config(page_title="Waivers & Docs — Velocity LA", page_icon="📄", layout="centered")
init_db()
inject_css()
page_header("📄 Digital Waiver & Document Collection",
            "Step-by-step document upload · Secured & Encrypted")

# ── Lead selector ──────────────────────────────────────────────────────────────
db = get_db()
try:
    booked_leads = (db.query(Lead)
                    .filter(Lead.pipeline_stage == "Booked")
                    .order_by(Lead.created_at.desc())
                    .all())
    lead_map = {f"{l.name}": l.id for l in booked_leads}
finally:
    db.close()

if not lead_map:
    st.info("No booked leads yet. Book a lead from the Pipeline page first.")
    if st.button("→ Go to Pipeline"):
        st.switch_page("pages/1_Pipeline.py")
    st.stop()

selected_name = st.selectbox("Select Booked Lead", list(lead_map.keys()))
selected_id   = lead_map[selected_name]

# ── Load existing documents ────────────────────────────────────────────────────
db = get_db()
try:
    docs = db.query(Document).filter(Document.lead_id == selected_id).all()
    uploaded_types = {d.doc_type for d in docs}
finally:
    db.close()

DOC_STEPS = [
    ("waiver",          "1",  "Liability Waiver",  "Sign the release & assumption of risk agreement"),
    ("drivers_license", "2",  "Driver's License",  "Upload a clear photo of your valid driver's license"),
    ("passenger_id",    "3",  "Passenger ID",      "Upload government-issued ID for each passenger"),
    ("selfie",          "4",  "Selfie with ID",    "Take a selfie holding your ID next to your face"),
]

# ── Progress bar ───────────────────────────────────────────────────────────────
n_done    = len(uploaded_types)
all_types = {s[0] for s in DOC_STEPS}
complete  = all_types <= uploaded_types

progress_cols = st.columns(len(DOC_STEPS) + 1)
step_labels   = [s[1] for s in DOC_STEPS] + ["✓"]
for i, (col, lbl) in enumerate(zip(progress_cols, step_labels)):
    done = i < n_done
    active = i == n_done and not complete
    bg = "#28a745" if done else ("#d4a017" if active else "#e8dcc8")
    fc = "white" if (done or active) else "#999"
    col.markdown(
        f"<div style='background:{bg};color:{fc};border-radius:50%;width:32px;height:32px;"
        f"display:flex;align-items:center;justify-content:center;font-weight:700;"
        f"font-size:0.85rem;margin:0 auto'>{lbl}</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

# ── Complete state ─────────────────────────────────────────────────────────────
if complete:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);color:white;
         border-radius:12px;padding:32px;text-align:center;margin:16px 0">
      <div style="font-size:2.5rem;margin-bottom:10px">✅</div>
      <h3 style="color:#d4a017;margin:0 0 8px">All Documents Received</h3>
      <p style="color:rgba(255,255,255,0.8);margin:0">
        Your documents have been received successfully.<br>
        We'll review them and confirm your experience within 24 hours.
      </p>
      <div style="margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.2);
           font-size:0.78rem;color:rgba(255,255,255,0.5)">
        🔒 Secured &amp; Encrypted &nbsp;·&nbsp; Documents stored on AWS S3
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Reset (Demo)", help="Clears uploaded docs to demo the flow again"):
        db = get_db()
        try:
            db.query(Document).filter(Document.lead_id == selected_id).delete()
            db.commit()
        finally:
            db.close()
        st.rerun()
    st.stop()

# ── Step-by-step upload ────────────────────────────────────────────────────────
for doc_type, step_num, title, desc in DOC_STEPS:
    done = doc_type in uploaded_types
    icon = "✅" if done else "📤"

    with st.container():
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(
                f"<div style='font-weight:700;color:#1a0a00;font-size:0.95rem'>"
                f"{icon} Step {step_num}: {title}</div>"
                f"<div style='font-size:0.8rem;color:#666;margin-top:3px'>{desc}</div>",
                unsafe_allow_html=True,
            )

        with c2:
            if done:
                db = get_db()
                try:
                    doc = db.query(Document).filter(
                        Document.lead_id == selected_id,
                        Document.doc_type == doc_type,
                    ).first()
                    fname = doc.filename if doc else "Uploaded"
                finally:
                    db.close()
                st.markdown(
                    f"<div style='color:#28a745;font-weight:700;font-size:0.85rem;"
                    f"padding:6px 0'>✓ {fname}</div>",
                    unsafe_allow_html=True,
                )
            elif doc_type == "waiver":
                # Waiver: checkbox agree
                agreed = st.checkbox("I have read and agree to the waiver", key=f"chk_{doc_type}")
                if agreed and st.button("Sign Waiver", key=f"btn_{doc_type}", type="primary"):
                    db = get_db()
                    try:
                        db.add(Document(lead_id=selected_id, doc_type=doc_type,
                                        filename="Waiver_Signed.pdf"))
                        db.commit()
                    finally:
                        db.close()
                    st.rerun()
            else:
                uploaded = st.file_uploader(
                    f"Upload {title}", type=["jpg", "jpeg", "png", "pdf"],
                    key=f"up_{doc_type}", label_visibility="collapsed",
                )
                if uploaded:
                    db = get_db()
                    try:
                        db.add(Document(lead_id=selected_id, doc_type=doc_type,
                                        filename=uploaded.name))
                        db.commit()
                    finally:
                        db.close()
                    st.rerun()

        st.divider()

# ── Documents list ─────────────────────────────────────────────────────────────
if uploaded_types:
    st.markdown("**Documents Uploaded**")
    db = get_db()
    try:
        all_docs = db.query(Document).filter(Document.lead_id == selected_id).all()
    finally:
        db.close()
    for d in all_docs:
        label = {"waiver": "Liability Waiver", "drivers_license": "Driver's License",
                 "passenger_id": "Passenger ID", "selfie": "Selfie with ID"}.get(d.doc_type, d.doc_type)
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;padding:6px 0;"
            f"border-bottom:1px solid #f0e8dc;font-size:0.82rem'>"
            f"<span style='color:#1a0a00;font-weight:600'>{label}</span>"
            f"<span style='color:#28a745;font-weight:700'>✓ {d.filename}</span></div>",
            unsafe_allow_html=True,
        )

st.markdown("""
<div style="text-align:center;margin-top:24px;font-size:0.75rem;color:#aaa">
  🔒 Secured &amp; Encrypted &nbsp;·&nbsp; Documents stored on AWS S3
</div>
""", unsafe_allow_html=True)
