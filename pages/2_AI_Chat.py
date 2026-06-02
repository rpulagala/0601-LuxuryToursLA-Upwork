import streamlit as st
from database import init_db, get_db, Lead, Conversation
from ai_agent import get_ai_response
from utils import inject_css, page_header, score_badge

st.set_page_config(page_title="AI Chat — Velocity LA", page_icon="🤖", layout="centered")
init_db()
inject_css()
page_header("🤖 AI Lead Qualification", "Maya qualifies the lead via SMS-style conversation and scores them 1–10")

# ── Lead selector ─────────────────────────────────────────────────────────────
db = get_db()
try:
    leads = (
        db.query(Lead)
        .filter(Lead.pipeline_stage.in_(["New Lead", "Contacted", "Qualified"]))
        .order_by(Lead.created_at.desc())
        .all()
    )
    lead_map = {f"{l.name}  ·  {l.pipeline_stage}": l.id for l in leads}
finally:
    db.close()

if not lead_map:
    st.info("No active leads yet — submit a lead form first.")
    if st.button("→ Go to Lead Form"):
        st.switch_page("pages/1_Lead_Form.py")
    st.stop()

current_id = st.session_state.get("current_lead_id")
keys = list(lead_map.keys())
default_idx = next((i for i, k in enumerate(keys) if lead_map[k] == current_id), 0)

selected_key = st.selectbox("Select lead", keys, index=default_idx)
selected_id  = lead_map[selected_key]
st.session_state.current_lead_id = selected_id

# ── Load lead + history ───────────────────────────────────────────────────────
db = get_db()
try:
    lead = db.query(Lead).filter(Lead.id == selected_id).first()
    history = (
        db.query(Conversation)
        .filter(Conversation.lead_id == selected_id)
        .order_by(Conversation.timestamp)
        .all()
    )
    msg_list  = [(m.role, m.message) for m in history]
    lead_info = {
        "name":    lead.name,
        "stage":   lead.pipeline_stage,
        "score":   lead.score,
        "car":     lead.preferred_car,
        "date":    lead.preferred_date,
        "group":   lead.group_size,
        "budget":  lead.budget,
    }
finally:
    db.close()

# ── Lead status bar ───────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown(f"**Lead:** {lead_info['name']}")
with c2:
    st.markdown(f"**Stage:** `{lead_info['stage']}`")
with c3:
    if lead_info["score"] > 0:
        st.markdown(score_badge(lead_info["score"]), unsafe_allow_html=True)

st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
for role, message in msg_list:
    with st.chat_message("assistant" if role == "assistant" else "user"):
        st.write(message)

# ── Qualified banner ──────────────────────────────────────────────────────────
if lead_info["stage"] == "Qualified":
    st.success(
        f"✅ **Qualified!** &nbsp;Score: {lead_info['score']:.0f}/10 &nbsp;|&nbsp; "
        f"Car: {lead_info['car']} &nbsp;|&nbsp; Date: {lead_info['date']} &nbsp;|&nbsp; "
        f"Group: {lead_info['group']} &nbsp;|&nbsp; Budget: {lead_info['budget']}"
    )
    if st.button("→ Send Booking Link", type="primary"):
        st.switch_page("pages/4_Booking.py")
    st.stop()

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input(f"Reply as {lead_info['name']}…")
if not user_input:
    st.stop()

# Save user message immediately and show it
db = get_db()
try:
    db.add(Conversation(lead_id=selected_id, role="user", message=user_input))
    db.commit()
finally:
    db.close()

with st.chat_message("user"):
    st.write(user_input)

# Get and save AI response
with st.chat_message("assistant"):
    with st.spinner("Maya is typing…"):
        response_text, qual_data = get_ai_response(selected_id, user_input)
    st.write(response_text)

db = get_db()
try:
    db.add(Conversation(lead_id=selected_id, role="assistant", message=response_text))
    if qual_data:
        lead = db.query(Lead).filter(Lead.id == selected_id).first()
        lead.preferred_car  = qual_data.get("car", lead.preferred_car)
        lead.preferred_date = qual_data.get("date", lead.preferred_date)
        lead.group_size     = str(qual_data.get("group_size", lead.group_size))
        lead.budget         = qual_data.get("budget", lead.budget)
        lead.score          = float(qual_data.get("score", 5))
        lead.pipeline_stage = "Qualified"
        lead.tag            = "Hot" if lead.score >= 8 else ("Warm" if lead.score >= 6 else "Cold")
    db.commit()
finally:
    db.close()

if qual_data:
    st.rerun()
