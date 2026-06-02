import streamlit as st
from datetime import datetime
from database import init_db, get_db, Lead, Conversation, NurtureEvent
from ai_agent import get_ai_response
from nurture import get_next_touch, log_nurture_event
from utils import inject_css, score_badge

st.set_page_config(page_title="Conversations — Velocity LA", page_icon="💬", layout="wide")
init_db()
inject_css()

# ── Load all leads + last message previews ────────────────────────────────────
db = get_db()
try:
    all_leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    lead_previews = {}
    for lead in all_leads:
        last = (db.query(Conversation)
                .filter(Conversation.lead_id == lead.id)
                .order_by(Conversation.timestamp.desc())
                .first())
        if last:
            preview = last.message[:55] + ("…" if len(last.message) > 55 else "")
        else:
            preview = "No messages yet"
        lead_previews[lead.id] = preview
finally:
    db.close()

# ── Selected lead ─────────────────────────────────────────────────────────────
current_id = st.session_state.get("current_lead_id")
if current_id is None and all_leads:
    current_id = all_leads[0].id
    st.session_state.current_lead_id = current_id


def _time_ago(dt):
    if not dt:
        return ""
    diff = datetime.utcnow() - dt
    if diff.days >= 1:
        return f"{diff.days}d ago"
    h = diff.seconds // 3600
    return f"{h} hrs ago" if h >= 1 else f"{diff.seconds // 60} min ago"


STAGE_COLORS = {
    "New Lead": "#6c757d", "Contacted": "#d4a017",
    "Qualified": "#8B4513", "Booked": "#28a745",
}

# ── 3-column layout ───────────────────────────────────────────────────────────
left_col, mid_col, right_col = st.columns([1, 2, 1], gap="small")

# ── LEFT: Inbox list ──────────────────────────────────────────────────────────
with left_col:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);color:white;
         padding:12px 14px;border-radius:8px;margin-bottom:10px;border-left:4px solid #d4a017">
      <div style="font-weight:800;font-size:0.95rem">💬 Conversations</div>
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.6);margin-top:2px">All leads</div>
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("Search", placeholder="Search leads…", label_visibility="collapsed")
    filtered = [l for l in all_leads if search.lower() in l.name.lower()] if search else all_leads

    for lead in filtered[:40]:
        is_sel = lead.id == current_id
        color  = STAGE_COLORS.get(lead.pipeline_stage, "#6c757d")
        ago    = _time_ago(lead.created_at)
        border = "2px solid #d4a017" if is_sel else "1px solid #e8dcc8"
        bg     = "#fdfaf5" if is_sel else "white"

        st.markdown(f"""
        <div style="background:{bg};border:{border};border-radius:7px;
             padding:9px 11px;margin-bottom:4px">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div style="font-weight:700;color:#1a0a00;font-size:0.83rem;
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px">{lead.name}</div>
            <div style="font-size:0.68rem;color:#aaa;white-space:nowrap;margin-left:4px">{ago}</div>
          </div>
          <div style="font-size:0.72rem;color:#888;margin-top:2px;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{lead_previews.get(lead.id,"")}</div>
          <div style="margin-top:4px">
            <span style="background:{color};color:white;padding:1px 7px;
                 border-radius:10px;font-size:0.65rem;font-weight:700">{lead.pipeline_stage}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Open", key=f"sel_{lead.id}", use_container_width=True):
            st.session_state.current_lead_id = lead.id
            st.rerun()

# ── Load selected lead data ───────────────────────────────────────────────────
if current_id:
    db = get_db()
    try:
        lead = db.query(Lead).filter(Lead.id == current_id).first()
        history = (db.query(Conversation)
                   .filter(Conversation.lead_id == current_id)
                   .order_by(Conversation.timestamp)
                   .all())
        nurture_history = (db.query(NurtureEvent)
                           .filter(NurtureEvent.lead_id == current_id)
                           .order_by(NurtureEvent.sent_at.desc())
                           .all())
        msg_list  = [(m.role, m.message) for m in history]
        lead_info = {
            "id":     lead.id,
            "name":   lead.name,
            "email":  lead.email,
            "phone":  lead.phone,
            "city":   lead.city or "Los Angeles, CA",
            "source": lead.source,
            "stage":  lead.pipeline_stage,
            "score":  lead.score,
            "car":    lead.preferred_car,
            "date":   lead.preferred_date,
            "group":  lead.group_size,
            "budget": lead.budget,
            "tag":    lead.tag,
        }
    finally:
        db.close()
else:
    lead_info = None
    msg_list  = []
    nurture_history = []

# ── MIDDLE: Chat ──────────────────────────────────────────────────────────────
with mid_col:
    if not lead_info:
        st.info("Select a lead from the inbox to start chatting.")
        st.stop()

    color = STAGE_COLORS.get(lead_info["stage"], "#6c757d")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);color:white;
         padding:12px 18px;border-radius:8px;margin-bottom:12px;
         display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-weight:800;font-size:1rem">{lead_info['name']}</div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.6)">{lead_info['city']}</div>
      </div>
      <div style="text-align:right">
        <span style="background:{color};color:white;padding:3px 12px;border-radius:12px;
             font-size:0.75rem;font-weight:700">{lead_info['stage']}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    chat_container = st.container(height=420)
    with chat_container:
        for role, message in msg_list:
            with st.chat_message("assistant" if role == "assistant" else "user"):
                st.write(message)

    # Qualified banner
    if lead_info["stage"] == "Qualified":
        st.success(
            f"✅ **Qualified!** &nbsp; Score: {lead_info['score']:.0f}/10 &nbsp;|&nbsp; "
            f"{lead_info['car']} &nbsp;|&nbsp; {lead_info['date']} &nbsp;|&nbsp; "
            f"Group: {lead_info['group']} &nbsp;|&nbsp; {lead_info['budget']}"
        )
        if st.button("📅 Send Booking Link", type="primary"):
            st.session_state._booking_lead_id = current_id
            st.switch_page("pages/1_Pipeline.py")
        st.stop()

    # Chat input
    user_input = st.chat_input(f"Reply as {lead_info['name'].split()[0]}…")
    if user_input:
        db = get_db()
        try:
            db.add(Conversation(lead_id=current_id, role="user", message=user_input))
            db.commit()
        finally:
            db.close()

        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Maya is typing…"):
                    response_text, qual_data = get_ai_response(current_id, user_input)
                st.write(response_text)

        db = get_db()
        try:
            db.add(Conversation(lead_id=current_id, role="assistant", message=response_text))
            if qual_data:
                upd = db.query(Lead).filter(Lead.id == current_id).first()
                upd.preferred_car  = qual_data.get("car", upd.preferred_car)
                upd.preferred_date = qual_data.get("date", upd.preferred_date)
                upd.group_size     = str(qual_data.get("group_size", upd.group_size))
                upd.budget         = qual_data.get("budget", upd.budget)
                upd.score          = float(qual_data.get("score", 5))
                upd.pipeline_stage = "Qualified"
                upd.tag            = "Hot" if upd.score >= 8 else ("Warm" if upd.score >= 6 else "Cold")
            db.commit()
        finally:
            db.close()

        if qual_data:
            st.rerun()

# ── RIGHT: Contact panel ──────────────────────────────────────────────────────
with right_col:
    if not lead_info:
        st.stop()

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);color:white;
         padding:12px 14px;border-radius:8px;margin-bottom:10px;border-left:4px solid #d4a017">
      <div style="font-weight:800;font-size:0.95rem">👤 Contact</div>
    </div>
    """, unsafe_allow_html=True)

    # Score badge
    badge = score_badge(lead_info["score"])
    st.markdown(badge, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

    # Tags
    tag_color = {"Hot": "#d4a017", "Warm": "#8B4513", "Cold": "#6c757d", "New": "#444"}.get(lead_info["tag"], "#444")
    tags_html = (
        f'<span style="background:{tag_color};color:white;padding:2px 10px;'
        f'border-radius:10px;font-size:0.72rem;font-weight:700;margin-right:4px">{lead_info["tag"]}</span>'
        f'<span style="background:#e8dcc8;color:#1a0a00;padding:2px 10px;'
        f'border-radius:10px;font-size:0.72rem;font-weight:700">{lead_info["stage"]}</span>'
    )
    st.markdown(tags_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    def _row(label, val):
        if val:
            st.markdown(
                f"<div style='font-size:0.75rem;color:#888;margin-bottom:1px'>{label}</div>"
                f"<div style='font-size:0.85rem;color:#1a0a00;font-weight:600;margin-bottom:8px'>{val}</div>",
                unsafe_allow_html=True,
            )

    _row("📧 Email",    lead_info["email"] or "—")
    _row("📞 Phone",   lead_info["phone"])
    _row("📍 City",    lead_info["city"])
    _row("🏎️ Car",     lead_info["car"] or "Not specified")
    _row("📅 Date",    lead_info["date"] or "Flexible")
    _row("👥 Group",   lead_info["group"] or "—")
    _row("💰 Budget",  lead_info["budget"] or "—")
    _row("📣 Source",  lead_info["source"])

    st.divider()

    # Nurture touch
    next_touch = get_next_touch(current_id)
    if next_touch:
        st.markdown(f"**Next Touch:** {next_touch['channel']} — _{next_touch['subject']}_")
        if st.button("📨 Send Touch", use_container_width=True):
            log_nurture_event(current_id, next_touch)
            st.success(f"Sent: {next_touch['subject']}")
            st.rerun()
    else:
        st.caption("All 7 nurture touches sent.")

    # Nurture history
    if nurture_history:
        st.markdown("**Nurture History**")
        for ev in nurture_history[:5]:
            ch_icon = "📱" if ev.channel == "SMS" else "✉️"
            st.markdown(
                f"<div style='font-size:0.72rem;color:#666;padding:3px 0;border-bottom:1px solid #f0e8dc'>"
                f"{ch_icon} Touch {ev.touch_number} — {ev.subject}</div>",
                unsafe_allow_html=True,
            )
