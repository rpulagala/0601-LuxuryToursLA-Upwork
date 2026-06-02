import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Booking
from utils import inject_css, page_header

st.set_page_config(page_title="Sales Tracking — Velocity LA", page_icon="📊", layout="wide")
init_db()
inject_css()
page_header("📊 Sales Tracking & Reporting", "Revenue, bookings, and team performance — last 30 days")

# ── Load data ─────────────────────────────────────────────────────────────────
db = get_db()
try:
    all_bookings = db.query(Booking).all()
    all_leads    = db.query(Lead).all()
finally:
    db.close()

total_revenue  = sum(b.price or 499.0 for b in all_bookings)
total_bookings = len(all_bookings)
aov            = total_revenue / total_bookings if total_bookings else 0
conversion     = total_bookings / len(all_leads) * 100 if all_leads else 0

# ── Top KPIs ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
def kpi(col, label, value, delta):
    col.markdown(f"""
    <div style="background:white;border:1px solid #e8dcc8;border-radius:8px;
         padding:18px 20px;text-align:center">
      <div style="font-size:1.9rem;font-weight:800;color:#d4a017;line-height:1">{value}</div>
      <div style="font-size:0.72rem;color:#888;text-transform:uppercase;letter-spacing:1px;margin-top:4px">{label}</div>
      <div style="font-size:0.75rem;color:#28a745;margin-top:4px">▲ {delta}</div>
    </div>
    """, unsafe_allow_html=True)

kpi(k1, "Total Sales",        f"${total_revenue:,.0f}",    "10.2%")
kpi(k2, "Total Bookings",     str(total_bookings),          "12.6%")
kpi(k3, "Avg Order Value",    f"${aov:,.0f}",               "4.7%")
kpi(k4, "Conversion Rate",    f"{conversion:.1f}%",         "2.1%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Revenue Over Time ─────────────────────────────────────────────────────────
chart_col, team_col = st.columns([3, 2], gap="medium")

with chart_col:
    st.markdown("#### Sales Over Time (Last 30 Days)")
    now = datetime.utcnow()
    days = [(now - timedelta(days=i)).date() for i in range(29, -1, -1)]
    rev_by_day = {d: 0.0 for d in days}
    for b in all_bookings:
        d = b.confirmed_at.date()
        if d in rev_by_day:
            rev_by_day[d] += b.price or 499.0

    df = pd.DataFrame({"Date": list(rev_by_day.keys()), "Revenue": list(rev_by_day.values())})
    fig = px.area(df, x="Date", y="Revenue",
                  color_discrete_sequence=["#d4a017"],
                  labels={"Revenue": "Revenue ($)", "Date": ""})
    fig.update_traces(line_width=2, fillcolor="rgba(212,160,23,0.15)")
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=280,
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0e8dc", tickprefix="$"),
        xaxis=dict(gridcolor="#f0e8dc"),
        font=dict(family="Segoe UI", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

with team_col:
    st.markdown("#### Sales by Team Member")

    # Aggregate by team member from booking data
    team_stats: dict[str, dict] = {}
    TEAM_MEMBERS = ["John Carter", "Mike Johnson", "Sarah Williams", "David Brown"]
    for tm in TEAM_MEMBERS:
        team_stats[tm] = {"sales": 0.0, "bookings": 0}
    for b in all_bookings:
        tm = b.team_member or "John Carter"
        if tm in team_stats:
            team_stats[tm]["sales"]    += b.price or 499.0
            team_stats[tm]["bookings"] += 1

    # Table header
    st.markdown("""
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr;
         background:#f5f0e8;padding:8px 12px;border-radius:6px 6px 0 0;
         font-size:0.75rem;font-weight:700;color:#1a0a00;margin-bottom:2px">
      <div>Team Member</div><div style="text-align:right">Sales</div>
      <div style="text-align:right">Bookings</div>
    </div>
    """, unsafe_allow_html=True)

    for tm, stats in team_stats.items():
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:2fr 1fr 1fr;
             padding:9px 12px;border-bottom:1px solid #f0e8dc;
             font-size:0.82rem;color:#1a0a00">
          <div style="font-weight:600">{tm}</div>
          <div style="text-align:right;color:#d4a017;font-weight:700">${stats['sales']:,.0f}</div>
          <div style="text-align:right">{stats['bookings']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Totals row
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr;
         padding:9px 12px;background:#f5f0e8;border-radius:0 0 6px 6px;
         font-size:0.82rem;font-weight:800;color:#1a0a00">
      <div>Total</div>
      <div style="text-align:right;color:#d4a017">${total_revenue:,.0f}</div>
      <div style="text-align:right">{total_bookings}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Car performance ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Revenue by Car")

car_rev: dict[str, float] = {}
for b in all_bookings:
    car_rev[b.car] = car_rev.get(b.car, 0.0) + (b.price or 499.0)

if car_rev:
    df_car = pd.DataFrame({
        "Car":     list(car_rev.keys()),
        "Revenue": list(car_rev.values()),
    }).sort_values("Revenue", ascending=False)

    fig_car = px.bar(
        df_car, x="Car", y="Revenue",
        color_discrete_sequence=["#d4a017", "#8B4513", "#3d1a00", "#b8860b", "#6c757d"],
        labels={"Revenue": "Revenue ($)", "Car": ""},
    )
    fig_car.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=240,
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#f0e8dc", tickprefix="$"),
        xaxis=dict(gridcolor="white"),
        font=dict(family="Segoe UI", size=12),
        showlegend=False,
    )
    fig_car.update_traces(marker_line_width=0)
    st.plotly_chart(fig_car, use_container_width=True)
