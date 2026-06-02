import streamlit as st
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Conversation, Booking
from ai_agent import get_opening_message
from utils import inject_css, score_badge

st.set_page_config(page_title="Pipeline — Velocity LA", page_icon="🏎️", layout="wide")
init_db()
inject_css()

STAGES = ["New Lead", "Contacted", "Qualified", "Booked"]
STAGE_COLORS = {
    "New Lead":  "#6c757d",
    "Contacted": "#d4a017",
    "Qualified": "#8B4513",
    "Booked":    "#28a745",
}
CARS = [
    "Lamborghini Huracán", "Ferrari 488 GTB", "McLaren 720S",
    "Porsche 911 GT3 RS", "Rolls-Royce Ghost",
]
PRICE_MAP = {
    "Lamborghini Huracán": 599, "Ferrari 488 GTB": 549,
    "McLaren 720S": 649, "Porsche 911 GT3 RS": 499, "Rolls-Royce Ghost": 449,
}
SOURCES   = ["Website", "Instagram", "TikTok", "Google Ads", "Friend / Referral"]
TIMESLOTS = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a00 0%,#3d1a00 100%);
     color:white;padding:18px 28px;border-radius:10px;margin-bottom:16px;
     border-left:5px solid #d4a017;">
  <h2 style="margin:0;font-size:1.3rem;font-weight:800;color:white">
    1. AI Powered Lead Capture &amp; Pipeline</h2>
  <p style="margin:5px 0 0;color:rgba(255,255,255,0.65);font-size:0.82rem">
    Luxury Driving Experiences Pipeline &nbsp;·&nbsp; Live CRM</p>
</div>
""", unsafe_allow_html=True)

# ── Toolbar ───────────────────────────────────────────────────────────────────
t1, t2 = st.columns([1, 5])
with t1:
    if st.button("＋  New Lead", type="primary", use_container_width=True):
        st.session_state._show_new_lead = not st.session_state.get("_show_new_lead", False)

# ── New Lead Form (inline below toolbar) ─────────────────────────────────────
if st.session_state.get("_show_new_lead"):
    with st.expander("New Lead", expanded=True):
        with st.form("new_lead_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name  = st.text_input("Full Name *", placeholder="Alex Johnson")
                phone = st.text_input("Phone *", placeholder="+1 (310) 555-0000")
            with c2:
                email = st.text_input("Email", placeholder="alex@example.com")
                city  = st.text_input("City", placeholder="Beverly Hills, CA")
            with c3:
                car    = st.selectbox("Car Interest", CARS)
                source = st.selectbox("Source", SOURCES)
            sub, cancel = st.columns(2)
            submitted = sub.form_submit_button("Create Lead", type="primary", use_container_width=True)
            cancelled = cancel.form_submit_button("Cancel", use_container_width=True)

        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Name and phone are required.")
            else:
                db = get_db()
                try:
                    lead = Lead(
                        name=name.strip(), phone=phone.strip(),
                        email=email.strip(), city=city.strip(),
                        source=source, preferred_car=car,
                        pipeline_stage="New Lead", tag="New",
                    )
                    db.add(lead); db.flush()
                    opening = get_opening_message(name.strip().split()[0])
                    db.add(Conversation(lead_id=lead.id, role="assistant", message=opening))
                    db.commit()
                    st.session_state.current_lead_id = lead.id
                    st.session_state._show_new_lead = False
                    st.success(f"✅ Lead created for {name.split()[0]}!")
                finally:
                    db.close()
                st.rerun()
        if cancelled:
            st.session_state._show_new_lead = False
            st.rerun()

# ── Load data ─────────────────────────────────────────────────────────────────
db = get_db()
try:
    all_leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    leads_by_stage = {s: [l for l in all_leads if l.pipeline_stage == s] for s in STAGES}
    stage_values   = {s: sum(PRICE_MAP.get(l.preferred_car, 499) for l in leads_by_stage[s]) for s in STAGES}
finally:
    db.close()


def _time_ago(dt):
    if not dt:
        return ""
    diff = datetime.utcnow() - dt
    if diff.days >= 1:
        return f"{diff.days}d ago"
    h = diff.seconds // 3600
    if h >= 1:
        return f"{h} hrs ago"
    return f"{diff.seconds // 60} min ago"


# ── Kanban board ──────────────────────────────────────────────────────────────
kanban_cols = st.columns(4, gap="small")

for col, stage in zip(kanban_cols, STAGES):
    color  = STAGE_COLORS[stage]
    leads  = leads_by_stage[stage]
    val    = stage_values[stage]

    with col:
        # Stage header
        st.markdown(f"""
        <div style="background:{color}22;border-top:3px solid {color};
             border-radius:6px 6px 0 0;padding:10px 12px;margin-bottom:0">
          <div style="font-weight:800;color:#1a0a00;font-size:0.9rem">{stage}</div>
          <div style="font-size:0.75rem;color:#666;margin-top:2px">
            {len(leads)} leads &nbsp;·&nbsp;
            <span style="color:{color};font-weight:700">${val:,.0f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Lead cards
        for lead in leads:
            price_val   = PRICE_MAP.get(lead.preferred_car, 499)
            price_label = f"${price_val:,}"
            ago         = _time_ago(lead.created_at)
            city_line   = lead.city or "Los Angeles, CA"
            badge_html  = score_badge(lead.score)
            car_short   = (lead.preferred_car or "—").replace("Lamborghini ", "Lambo ").replace("Rolls-Royce ", "RR ")

            st.markdown(f"""
            <div style="background:white;border:1px solid #e8dcc8;border-left:3px solid {color};
                 border-radius:0 0 6px 6px;padding:11px 12px;margin-bottom:2px">
              <div style="font-weight:700;color:#1a0a00;font-size:0.88rem;
                   white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{lead.name}</div>
              <div style="font-size:0.73rem;color:#888;margin-top:1px">{city_line}</div>
              <div style="font-size:0.73rem;color:#666;margin-top:2px">🏎️ {car_short}</div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-top:7px">
                <span style="font-weight:800;color:#d4a017;font-size:0.88rem">{price_label}</span>
                <span style="font-size:0.7rem;color:#aaa">{ago}</span>
              </div>
              <div style="margin-top:6px">{badge_html}</div>
            </div>
            """, unsafe_allow_html=True)

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("💬 Chat", key=f"chat_{lead.id}", use_container_width=True):
                    st.session_state.current_lead_id = lead.id
                    st.switch_page("pages/2_Conversations.py")
            with btn2:
                if stage in ("New Lead", "Contacted", "Qualified"):
                    label = "📅 Book" if stage == "Qualified" else "→ Qualify"
                    if st.button(label, key=f"act_{lead.id}", use_container_width=True):
                        if stage == "Qualified":
                            st.session_state._booking_lead_id = lead.id
                            st.rerun()
                        else:
                            st.session_state.current_lead_id = lead.id
                            st.switch_page("pages/2_Conversations.py")
                else:
                    if st.button("✅ Booked", key=f"act_{lead.id}", use_container_width=True, disabled=True):
                        pass

            st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

# ── Inline booking modal ───────────────────────────────────────────────────────
if booking_id := st.session_state.get("_booking_lead_id"):
    db = get_db()
    try:
        blead = db.query(Lead).filter(Lead.id == booking_id).first()
        blead_name = blead.name if blead else "Unknown"
        blead_car  = blead.preferred_car if blead else CARS[0]
    finally:
        db.close()

    st.divider()
    st.markdown(f"### 📅 Book Slot — {blead_name}")
    available_dates = [
        (datetime.today() + timedelta(days=i)).strftime("%a, %b %d")
        for i in range(1, 15)
        if (datetime.today() + timedelta(days=i)).weekday() != 0
    ]
    b1, b2, b3 = st.columns(3)
    car_idx = CARS.index(blead_car) if blead_car in CARS else 0
    with b1: car_choice  = st.selectbox("Car", CARS, index=car_idx, key="bk_car")
    with b2: date_choice = st.selectbox("Date", available_dates, key="bk_date")
    with b3: time_choice = st.selectbox("Time", TIMESLOTS, key="bk_time")

    price_val = PRICE_MAP[car_choice]
    st.info(f"**Deposit:** ${price_val} &nbsp;·&nbsp; Balance due on arrival")

    ok, cancel = st.columns(2)
    with ok:
        if st.button(f"✅ Confirm Booking — ${price_val}", type="primary", use_container_width=True):
            db = get_db()
            try:
                db.add(Booking(
                    lead_id=booking_id, slot_date=date_choice,
                    slot_time=time_choice, car=car_choice,
                    amount=f"${price_val}", price=float(price_val),
                ))
                blead_obj = db.query(Lead).filter(Lead.id == booking_id).first()
                blead_obj.pipeline_stage = "Booked"
                blead_obj.preferred_car  = car_choice
                db.add(Conversation(
                    lead_id=booking_id, role="assistant",
                    message=(f"You're all set, {blead_obj.name.split()[0]}! 🎉 "
                             f"{car_choice} confirmed for {date_choice} at {time_choice}. See you on the road!"),
                ))
                db.commit()
            finally:
                db.close()
            st.session_state._booking_lead_id = None
            st.balloons()
            st.rerun()
    with cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state._booking_lead_id = None
            st.rerun()
