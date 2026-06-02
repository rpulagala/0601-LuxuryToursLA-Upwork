import streamlit as st
from database import init_db, get_db, Lead, Booking
from utils import inject_css, metric_card

st.set_page_config(
    page_title="Velocity LA — AI Demo",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# Auto-seed on first load (handles Streamlit Cloud ephemeral filesystem)
_db = get_db()
_empty = _db.query(Lead).count() == 0
_db.close()
if _empty:
    import random
    random.seed(42)
    from seed_data import seed
    seed()

if "current_lead_id" not in st.session_state:
    st.session_state.current_lead_id = None

inject_css()

# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1a0a00 0%, #3d1a00 50%, #1a0a00 100%);
         padding: 56px 40px 48px; border-radius: 12px; margin-bottom: 28px; text-align: center; position: relative; overflow: hidden;">
        <div style="display:inline-block; background:#d4a017; color:white; font-size:10px;
             font-weight:700; letter-spacing:2px; padding:4px 14px; border-radius:4px;
             margin-bottom:18px; text-transform:uppercase;">Live Client Demo</div>
        <h1 style="color:white; font-size:2.2rem; font-weight:800; margin:0 0 10px; line-height:1.2;">
            Velocity LA &nbsp;<span style="color:#d4a017;">AI Automation</span>&nbsp; System
        </h1>
        <p style="color:rgba(255,255,255,0.72); font-size:0.97rem; max-width:580px; margin:0 auto;">
            A fully automated AI-powered customer journey — from first lead touch to confirmed booking.
            Built with Python · Streamlit · Google Gemini · SQLite.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Live metrics ─────────────────────────────────────────────────────────────
db = get_db()
try:
    total_leads = db.query(Lead).count()
    qualified   = db.query(Lead).filter(Lead.pipeline_stage == "Qualified").count()
    booked      = db.query(Lead).filter(Lead.pipeline_stage == "Booked").count()
    deposits    = db.query(Booking).count()
finally:
    db.close()

c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Total Leads",  total_leads, "👥")
with c2: metric_card("AI Qualified", qualified,   "🤖")
with c3: metric_card("Booked",       booked,      "✅")
with c4: metric_card("Deposits",     deposits,    "💳")

st.markdown("<br>", unsafe_allow_html=True)

# ── Demo flow guide ───────────────────────────────────────────────────────────
st.markdown("### How This Demo Works")
steps = [
    ("1️⃣", "Lead Form",      "Fill the prospect form — simulates a website or Instagram ad submission."),
    ("2️⃣", "AI Chat",        "AI instantly qualifies the lead via SMS conversation and scores them 1–10."),
    ("3️⃣", "CRM Dashboard",  "See all leads on a live pipeline board. Simulate nurture email/SMS touches."),
    ("4️⃣", "Booking",        "Qualified leads get a booking link — pick a slot, confirm the deposit."),
]
cols = st.columns(4)
for col, (icon, title, desc) in zip(cols, steps):
    with col:
        st.markdown(
            f"""<div style="background:white; border:1px solid #e8dcc8; border-radius:8px;
                 padding:16px; text-align:center; min-height:130px;">
                <div style="font-size:1.7rem">{icon}</div>
                <div style="font-weight:700; color:#1a0a00; margin:6px 0 4px; font-size:0.95rem">{title}</div>
                <div style="font-size:0.78rem; color:#666; line-height:1.4">{desc}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the sidebar to navigate through the demo steps.")
