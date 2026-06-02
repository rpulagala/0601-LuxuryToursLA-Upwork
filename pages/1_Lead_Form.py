import streamlit as st
from database import init_db, get_db, Lead, Conversation
from ai_agent import get_opening_message
from utils import inject_css, page_header

st.set_page_config(page_title="Lead Form — Velocity LA", page_icon="📋", layout="centered")
init_db()
inject_css()
page_header("📋 Lead Capture Form", "Simulates a website embed or Instagram lead-ad form")

CARS = [
    "Lamborghini Huracán",
    "Ferrari 488 GTB",
    "McLaren 720S",
    "Porsche 911 GT3 RS",
    "Rolls-Royce Ghost",
    "Not sure yet — surprise me",
]
SOURCES = ["Website", "Instagram", "TikTok", "Google Ads", "Friend / Referral", "Other"]

# ── Form ─────────────────────────────────────────────────────────────────────
with st.form("lead_form", clear_on_submit=True):
    st.markdown("#### Book Your Dream Drive in Los Angeles")
    st.markdown(
        "<small>Fill in your details and our AI will reach out to help plan your experience.</small>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="Alex Johnson")
    with col2:
        phone = st.text_input("Phone Number *", placeholder="+1 (310) 555-0000")

    email = st.text_input("Email Address", placeholder="alex@example.com")

    col3, col4 = st.columns(2)
    with col3:
        preferred_car = st.selectbox("Which car interests you?", CARS)
    with col4:
        source = st.selectbox("How did you hear about us?", SOURCES)

    submitted = st.form_submit_button("🏎️  Request My Experience", use_container_width=True)

# ── On submit ────────────────────────────────────────────────────────────────
if submitted:
    if not name.strip() or not phone.strip():
        st.error("Name and phone number are required.")
    else:
        db = get_db()
        try:
            lead = Lead(
                name=name.strip(),
                phone=phone.strip(),
                email=email.strip(),
                source=source,
                preferred_car="" if "surprise" in preferred_car else preferred_car,
                pipeline_stage="Contacted",
                tag="New",
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)

            opening = get_opening_message(name.strip().split()[0])
            db.add(Conversation(lead_id=lead.id, role="assistant", message=opening))
            db.commit()

            st.session_state.current_lead_id = lead.id
            st.session_state._form_success = name.strip().split()[0]
        finally:
            db.close()

if first_name := st.session_state.pop("_form_success", None):
    st.success(f"✅ Lead created for **{first_name}**. Maya has sent an opening message.")
    st.markdown("**Next:** Head to the AI Chat page to continue the qualification conversation.")
    if st.button("→ Go to AI Chat"):
        st.switch_page("pages/2_AI_Chat.py")
