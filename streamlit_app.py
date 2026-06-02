import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Booking

st.set_page_config(
    page_title="Velocity LA — Executive Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# Auto-seed on first load
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

from utils import inject_css
inject_css()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a00 0%,#3d1a00 50%,#1a0a00 100%);
     padding:40px 40px 36px;border-radius:12px;margin-bottom:24px;text-align:center;">
  <div style="display:inline-block;background:#d4a017;color:white;font-size:10px;
       font-weight:700;letter-spacing:2px;padding:4px 14px;border-radius:4px;
       margin-bottom:14px;text-transform:uppercase">Executive Dashboard</div>
  <h1 style="color:white;font-size:2rem;font-weight:800;margin:0 0 8px;line-height:1.2">
    Velocity LA &nbsp;<span style="color:#d4a017">AI Automation</span>&nbsp; System
  </h1>
  <p style="color:rgba(255,255,255,0.65);font-size:0.9rem;max-width:560px;margin:0 auto">
    Full-funnel overview — leads, revenue, bookings, and conversion performance.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
db = get_db()
try:
    all_leads    = db.query(Lead).all()
    all_bookings = db.query(Booking).all()
finally:
    db.close()

total_leads    = len(all_leads)
total_bookings = len(all_bookings)
total_revenue  = sum(b.price or 499.0 for b in all_bookings)
aov            = total_revenue / total_bookings if total_bookings else 0
qualified      = sum(1 for l in all_leads if l.pipeline_stage in ("Qualified", "Booked"))
conversion_pct = f"{total_bookings / total_leads * 100:.1f}%" if total_leads else "0%"

# ── Top KPI metrics ───────────────────────────────────────────────────────────
from utils import metric_card
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Total Revenue",    f"${total_revenue:,.0f}", "💰")
with c2: metric_card("Total Bookings",   total_bookings,           "📅")
with c3: metric_card("Avg Order Value",  f"${aov:,.0f}",           "💳")
with c4: metric_card("Conversion Rate",  conversion_pct,           "📈")

st.markdown("<br>", unsafe_allow_html=True)

# ── Revenue Over Time ─────────────────────────────────────────────────────────
left_chart, right_chart = st.columns([3, 2], gap="medium")

with left_chart:
    st.markdown("#### Revenue Over Time")

    now = datetime.utcnow()
    days_30 = [(now - timedelta(days=i)).date() for i in range(29, -1, -1)]
    rev_by_day = {d: 0.0 for d in days_30}
    for b in all_bookings:
        d = b.confirmed_at.date()
        if d in rev_by_day:
            rev_by_day[d] += b.price or 499.0

    df_rev = pd.DataFrame({
        "Date":    list(rev_by_day.keys()),
        "Revenue": list(rev_by_day.values()),
    })
    df_rev["Cumulative"] = df_rev["Revenue"].cumsum()

    fig_rev = px.line(
        df_rev, x="Date", y="Cumulative",
        labels={"Cumulative": "Revenue ($)", "Date": ""},
        color_discrete_sequence=["#d4a017"],
    )
    fig_rev.update_traces(line_width=2.5, fill="tozeroy",
                          fillcolor="rgba(212,160,23,0.12)")
    fig_rev.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=260,
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0e8dc", tickprefix="$"),
        xaxis=dict(gridcolor="#f0e8dc"),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

with right_chart:
    st.markdown("#### Bookings by Car")

    car_counts: dict[str, int] = {}
    for b in all_bookings:
        car_counts[b.car] = car_counts.get(b.car, 0) + 1

    if car_counts:
        short = {
            "Lamborghini Huracán": "Lamborghini",
            "Ferrari 488 GTB":     "Ferrari",
            "McLaren 720S":        "McLaren",
            "Porsche 911 GT3 RS":  "Porsche",
            "Rolls-Royce Ghost":   "Rolls-Royce",
        }
        labels = [short.get(k, k) for k in car_counts]
        values = list(car_counts.values())
        colors = ["#d4a017", "#8B4513", "#3d1a00", "#b8860b", "#6c757d"]

        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.55,
            marker_colors=colors,
            textinfo="percent",
            hovertemplate="%{label}: %{value} bookings<extra></extra>",
        ))
        fig_pie.update_layout(
            margin=dict(l=0, r=0, t=10, b=0), height=260,
            paper_bgcolor="white",
            legend=dict(font=dict(size=11), orientation="v"),
            font=dict(family="Segoe UI"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ── Conversion Funnel + Top Sources ───────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
funnel_col, source_col = st.columns(2, gap="medium")

with funnel_col:
    st.markdown("#### Conversion Funnel")

    booked_count = sum(1 for l in all_leads if l.pipeline_stage == "Booked")
    paid_count   = total_bookings   # all bookings have a deposit
    stages_funnel = [
        ("Leads",     total_leads,    "#6c757d"),
        ("Qualified", qualified,      "#d4a017"),
        ("Booked",    booked_count,   "#8B4513"),
        ("Paid",      paid_count,     "#28a745"),
    ]
    for label, count, color in stages_funnel:
        pct = count / total_leads * 100 if total_leads else 0
        st.markdown(f"""
        <div style="display:flex;align-items:center;margin-bottom:10px">
          <div style="width:80px;font-size:0.8rem;color:#555;font-weight:600">{label}</div>
          <div style="flex:1;background:#f0e8dc;border-radius:4px;height:22px;position:relative;margin:0 10px">
            <div style="background:{color};width:{pct:.0f}%;height:100%;border-radius:4px"></div>
          </div>
          <div style="width:50px;text-align:right;font-size:0.82rem;font-weight:700;color:{color}">{count}</div>
          <div style="width:50px;text-align:right;font-size:0.75rem;color:#888">({pct:.0f}%)</div>
        </div>
        """, unsafe_allow_html=True)

with source_col:
    st.markdown("#### Top Lead Sources")

    source_counts: dict[str, int] = {}
    for l in all_leads:
        src = l.source or "Unknown"
        source_counts[src] = source_counts.get(src, 0) + 1

    if source_counts:
        df_src = pd.DataFrame({
            "Source": list(source_counts.keys()),
            "Leads":  list(source_counts.values()),
        }).sort_values("Leads", ascending=True)

        fig_bar = px.bar(
            df_src, x="Leads", y="Source", orientation="h",
            color_discrete_sequence=["#d4a017"],
            labels={"Leads": "", "Source": ""},
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=10, b=0), height=230,
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(gridcolor="#f0e8dc"),
            yaxis=dict(gridcolor="white"),
            font=dict(family="Segoe UI", size=12),
        )
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the sidebar to navigate through the demo steps.")
