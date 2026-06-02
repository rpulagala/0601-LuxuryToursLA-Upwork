import streamlit as st
from database import init_db, get_db, Lead, Conversation, Booking, NurtureEvent
from nurture import get_next_touch, log_nurture_event
from utils import inject_css, page_header, score_badge, metric_card

st.set_page_config(page_title="CRM Dashboard — Velocity LA", page_icon="📊", layout="wide")
init_db()
inject_css()
page_header("📊 CRM Pipeline Dashboard", "Live view of all leads · click 📨 to simulate a nurture touch")

STAGES = ["New Lead", "Contacted", "Qualified", "Booked"]

# ── Load all data ─────────────────────────────────────────────────────────────
db = get_db()
try:
    all_leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    nurture_sent = {
        l.id: db.query(NurtureEvent).filter(NurtureEvent.lead_id == l.id).count()
        for l in all_leads
    }
    leads_by_stage = {s: [l for l in all_leads if l.pipeline_stage == s] for s in STAGES}

    total      = len(all_leads)
    qualified  = len(leads_by_stage["Qualified"])
    booked     = len(leads_by_stage["Booked"])
    hot_count  = sum(1 for l in all_leads if l.score >= 8)

    recent_events = (
        db.query(NurtureEvent, Lead)
        .join(Lead)
        .order_by(NurtureEvent.sent_at.desc())
        .limit(8)
        .all()
    )
    event_log = [
        {
            "name":    lead.name,
            "touch":   ev.touch_number,
            "channel": ev.channel,
            "subject": ev.subject,
            "time":    ev.sent_at.strftime("%H:%M:%S"),
        }
        for ev, lead in recent_events
    ]
finally:
    db.close()

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1: metric_card("Total Leads",  total,     "👥")
with m2: metric_card("Qualified",    qualified, "🤖")
with m3: metric_card("Booked",       booked,    "✅")
with m4: metric_card("Hot Leads",    hot_count, "🔥")

st.divider()

# ── Kanban ────────────────────────────────────────────────────────────────────
stage_cols = st.columns(4)

for col, stage in zip(stage_cols, STAGES):
    stage_leads = leads_by_stage[stage]
    with col:
        st.markdown(f"**{stage}** &nbsp;`{len(stage_leads)}`")

        if not stage_leads:
            st.markdown(
                '<div style="background:#f9f9f9;border:1px dashed #ccc;border-radius:6px;'
                'padding:14px;text-align:center;color:#bbb;font-size:0.8rem;">Empty</div>',
                unsafe_allow_html=True,
            )

        for lead in stage_leads:
            badge     = score_badge(lead.score)
            car_label = f"🏎️ {lead.preferred_car}" if lead.preferred_car else "🏎️ Car TBD"
            sent      = nurture_sent.get(lead.id, 0)

            st.markdown(
                f"""<div class="lead-card">
                    <div class="lead-card-name">{lead.name}</div>
                    <div class="lead-card-detail">{car_label}</div>
                    <div class="lead-card-detail">📱 {lead.phone or "—"}</div>
                    <div style="margin-top:6px">{badge}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("💬 Chat", key=f"chat_{lead.id}", use_container_width=True):
                    st.session_state.current_lead_id = lead.id
                    st.switch_page("pages/2_AI_Chat.py")

            with btn2:
                next_touch = get_next_touch(lead.id)
                if next_touch and stage != "Booked":
                    label = f"📨 T{sent + 1}"
                    tip   = f"{next_touch['channel']} — {next_touch['subject']}"
                    if st.button(label, key=f"nurture_{lead.id}", use_container_width=True, help=tip):
                        log_nurture_event(lead.id, next_touch)
                        st.rerun()
                else:
                    st.button("✓ Done", key=f"done_{lead.id}", use_container_width=True, disabled=True)

# ── Nurture event log ─────────────────────────────────────────────────────────
st.divider()
st.markdown("### Recent Nurture Activity")

if not event_log:
    st.info("No nurture events yet. Press a 📨 button above to simulate sending a touch.")
else:
    for ev in event_log:
        icon = "📱" if ev["channel"] == "SMS" else "📧"
        st.markdown(
            f"{icon} &nbsp;**{ev['name']}** — Touch #{ev['touch']} "
            f"({ev['channel']}): *{ev['subject']}* — `{ev['time']}`"
        )

# ── Demo controls ─────────────────────────────────────────────────────────────
st.divider()
ctrl1, ctrl2 = st.columns(2)

with ctrl1:
    if st.button("🎬  Load Sample Data", use_container_width=True):
        from seed_data import seed
        seed()
        st.session_state.current_lead_id = None
        st.success("Sample data loaded — 5 leads across all pipeline stages.")
        st.rerun()

with ctrl2:
    if st.button("🗑️  Reset All Demo Data", type="secondary", use_container_width=True):
        db = get_db()
        try:
            db.query(NurtureEvent).delete()
            db.query(Conversation).delete()
            db.query(Booking).delete()
            db.query(Lead).delete()
            db.commit()
            st.session_state.current_lead_id = None
        finally:
            db.close()
        st.success("All demo data cleared.")
        st.rerun()
