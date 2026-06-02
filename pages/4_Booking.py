import streamlit as st
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Booking, Conversation
from utils import inject_css, page_header, score_badge

st.set_page_config(page_title="Booking — Velocity LA", page_icon="📅", layout="centered")
init_db()
inject_css()
page_header("📅 Booking Funnel", "Slot picker + mock deposit confirmation — no real payment")

CARS = [
    "Lamborghini Huracán",
    "Ferrari 488 GTB",
    "McLaren 720S",
    "Porsche 911 GT3 RS",
    "Rolls-Royce Ghost",
]
TIME_SLOTS = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
PRICES = {
    "Lamborghini Huracán":  "$599",
    "Ferrari 488 GTB":      "$549",
    "McLaren 720S":         "$649",
    "Porsche 911 GT3 RS":   "$499",
    "Rolls-Royce Ghost":    "$449",
}

# Dates: next 14 days, skip Mondays
available_dates = [
    (datetime.today() + timedelta(days=i)).strftime("%a, %b %d")
    for i in range(1, 15)
    if (datetime.today() + timedelta(days=i)).weekday() != 0
]

# ── Recent confirmed bookings ────────────────────────────────────────────────
db = get_db()
try:
    booked = (
        db.query(Lead, Booking)
        .join(Booking)
        .filter(Lead.pipeline_stage == "Booked")
        .order_by(Booking.confirmed_at.desc())
        .all()
    )
    booked_list = [
        {
            "name": l.name,
            "car":  b.car,
            "date": b.slot_date,
            "time": b.slot_time,
            "amt":  b.amount,
            "when": b.confirmed_at.strftime("%b %d, %Y %H:%M"),
        }
        for l, b in booked
    ]
    eligible = (
        db.query(Lead)
        .filter(Lead.pipeline_stage.in_(["New Lead", "Contacted", "Qualified"]))
        .order_by(Lead.score.desc())
        .all()
    )
    lead_map = {f"{l.name}  (Score: {l.score:.0f}  ·  {l.pipeline_stage})": l.id for l in eligible}
finally:
    db.close()

if booked_list:
    st.markdown("### Confirmed Bookings")
    for b in booked_list:
        st.success(
            f"✅ **{b['name']}** — {b['car']} &nbsp;·&nbsp; {b['date']} at {b['time']} "
            f"&nbsp;·&nbsp; Deposit: {b['amt']} &nbsp;·&nbsp; *{b['when']}*"
        )
    st.divider()

# ── New booking form ──────────────────────────────────────────────────────────
st.markdown("### New Booking")

if not lead_map:
    st.info("No leads available. Create a lead and run the AI chat first.")
    if st.button("→ Go to Lead Form"):
        st.switch_page("pages/1_Lead_Form.py")
    st.stop()

current_id = st.session_state.get("current_lead_id")
keys       = list(lead_map.keys())
default    = next((i for i, k in enumerate(keys) if lead_map[k] == current_id), 0)

selected_key = st.selectbox("Select lead to book", keys, index=default)
selected_id  = lead_map[selected_key]

db = get_db()
try:
    lead = db.query(Lead).filter(Lead.id == selected_id).first()
    linfo = {
        "name":   lead.name,
        "car":    lead.preferred_car,
        "budget": lead.budget,
        "group":  lead.group_size,
        "score":  lead.score,
        "date":   lead.preferred_date,
    }
finally:
    db.close()

# Lead summary
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Lead:** {linfo['name']}")
    st.markdown(f"**Preferred car:** {linfo['car'] or '—'}")
    st.markdown(f"**Group size:** {linfo['group'] or '—'}")
with c2:
    st.markdown(f"**Budget:** {linfo['budget'] or '—'}")
    st.markdown(f"**Preferred date:** {linfo['date'] or 'Flexible'}")
    if linfo["score"] > 0:
        st.markdown(score_badge(linfo["score"]), unsafe_allow_html=True)

st.divider()

# Booking selectors
b1, b2, b3 = st.columns(3)
with b1:
    car_default = CARS.index(linfo["car"]) if linfo["car"] in CARS else 0
    car_choice  = st.selectbox("Car", CARS, index=car_default)
with b2:
    date_choice = st.selectbox("Date", available_dates)
with b3:
    time_choice = st.selectbox("Time", TIME_SLOTS)

price = PRICES[car_choice]

st.markdown(
    f"""<div style="background:#faf7f2; border:1px solid #e8dcc8; border-radius:8px;
         padding:16px 20px; margin:14px 0;">
        <div style="font-weight:700; color:#1a0a00; margin-bottom:8px;">Booking Summary</div>
        <div style="font-size:0.9rem; color:#444; line-height:1.8">
            🏎️ &nbsp;{car_choice}<br>
            📅 &nbsp;{date_choice} at {time_choice}<br>
            👤 &nbsp;{linfo['name']}<br>
            💳 &nbsp;Deposit: <strong style="color:#d4a017">{price}</strong>
            &nbsp;<span style="font-size:0.8rem;color:#888">(balance due on arrival)</span>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

if st.button(f"✅  Confirm Booking — Pay {price} Deposit", type="primary", use_container_width=True):
    db = get_db()
    try:
        db.add(Booking(
            lead_id=selected_id,
            slot_date=date_choice,
            slot_time=time_choice,
            car=car_choice,
            amount=price,
        ))
        lead = db.query(Lead).filter(Lead.id == selected_id).first()
        lead.pipeline_stage = "Booked"
        lead.preferred_car  = car_choice
        db.add(Conversation(
            lead_id=selected_id,
            role="assistant",
            message=(
                f"You're all set, {lead.name.split()[0]}! 🎉 "
                f"Your {car_choice} experience is confirmed for {date_choice} at {time_choice}. "
                "We'll send a reminder 48 hours before. See you on the road!"
            ),
        ))
        db.commit()
        st.session_state._booking_done = {
            "name": lead.name, "car": car_choice,
            "date": date_choice, "time": time_choice, "price": price,
        }
    finally:
        db.close()
    st.rerun()

if b := st.session_state.pop("_booking_done", None):
    st.balloons()
    st.markdown(
        f"""<div class="booking-confirm">
            <div style="font-size:2rem;margin-bottom:8px">🏎️</div>
            <h3>Booking Confirmed!</h3>
            <p>{b['name']} &nbsp;·&nbsp; {b['car']}<br>
               {b['date']} at {b['time']}<br>
               Deposit: {b['price']}</p>
            <div class="sub">
                📩 Confirmation SMS sent &nbsp;·&nbsp;
                📄 Waiver follows next &nbsp;·&nbsp;
                📸 Photo package included
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
