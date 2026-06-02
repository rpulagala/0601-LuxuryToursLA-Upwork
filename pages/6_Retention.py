import streamlit as st
from utils import inject_css, page_header

st.set_page_config(page_title="Retention — Velocity LA", page_icon="🔄", layout="wide")
inject_css()
page_header("🔄 Customer Retention Automation",
            "Anniversary, re-engagement, and promotional campaigns — running automatically")

# ── Tab selector ──────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📅 Anniversary & Loyalty", "🔃 Re-engagement"])

CAMPAIGNS_ANNIV = [
    {"name": "1-Year Anniversary Drive",        "status": "Active", "next": "May 18, 2024", "recipients": 142},
    {"name": "Birthday Month Surprise",          "status": "Active", "next": "May 20, 2024", "recipients": 98},
    {"name": "VIP 3-Booking Milestone",          "status": "Active", "next": "May 25, 2024", "recipients": 156},
    {"name": "Holiday Promo — Dec",             "status": "Draft",  "next": "Dec 01, 2024", "recipients": 312},
]

CAMPAIGNS_REENG = [
    {"name": "90-Day Lapsed Follow-up",         "status": "Active", "next": "May 22, 2024", "recipients": 87},
    {"name": "Price Drop Alert — Porsche",      "status": "Active", "next": "May 28, 2024", "recipients": 63},
    {"name": "\"We Miss You\" Win-Back",        "status": "Active", "next": "Jun 04, 2024", "recipients": 201},
    {"name": "New Car Added — McLaren 750S",    "status": "Draft",  "next": "TBD",          "recipients": 0},
]

def campaign_table(campaigns):
    # Header
    st.markdown("""
    <div style="display:grid;grid-template-columns:3fr 1fr 1.5fr 1fr;
         background:#f5f0e8;padding:9px 14px;border-radius:6px 6px 0 0;
         font-size:0.75rem;font-weight:700;color:#1a0a00;margin-bottom:2px">
      <div>Campaign</div><div>Status</div>
      <div>Next Run</div><div style="text-align:right">Recipients</div>
    </div>
    """, unsafe_allow_html=True)

    for c in campaigns:
        status_color = "#28a745" if c["status"] == "Active" else "#888"
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:3fr 1fr 1.5fr 1fr;
             padding:10px 14px;border-bottom:1px solid #f0e8dc;
             font-size:0.82rem;color:#1a0a00;background:white">
          <div style="font-weight:600">{c['name']}</div>
          <div><span style="background:{status_color};color:white;padding:2px 9px;
               border-radius:10px;font-size:0.7rem;font-weight:700">{c['status']}</span></div>
          <div style="color:#555">{c['next']}</div>
          <div style="text-align:right;font-weight:700;color:#d4a017">{c['recipients']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
    if st.button("＋ New Campaign", key=f"new_{campaigns[0]['name'][:8]}"):
        st.info("Campaign builder would open here (GoHighLevel integration).")

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    campaign_table(CAMPAIGNS_ANNIV)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    campaign_table(CAMPAIGNS_REENG)

# ── Email preview ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.markdown("#### Campaign Preview — 1-Year Anniversary")

preview_col, stat_col = st.columns([2, 1], gap="large")

with preview_col:
    st.markdown("""
    <div style="border:1px solid #e8dcc8;border-radius:12px;overflow:hidden;max-width:460px">
      <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);padding:20px 24px;">
        <img src="https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&h=180&fit=crop"
             style="width:100%;border-radius:8px;object-fit:cover;height:140px" onerror="this.style.display='none'">
      </div>
      <div style="padding:24px;">
        <h3 style="color:#1a0a00;margin:0 0 10px;font-size:1.1rem">Happy Anniversary! 🎉</h3>
        <p style="color:#555;font-size:0.85rem;line-height:1.7;margin:0 0 16px">
          It's been a year since your amazing driving experience with us!
          We hope to see you back soon for another unforgettable adventure.<br><br>
          As a loyal Velocity LA guest, you get <strong>15% off</strong> your next booking —
          no code needed, just mention this email.
        </p>
        <a href="#" style="display:inline-block;background:#d4a017;color:white;
           padding:10px 22px;border-radius:6px;text-decoration:none;
           font-weight:700;font-size:0.85rem">
          Book Your Next Experience →
        </a>
        <p style="margin-top:16px;color:#aaa;font-size:0.72rem">
          Maya | Velocity LA &nbsp;·&nbsp; Unsubscribe
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

with stat_col:
    st.markdown("**Campaign Stats**")
    for label, val, color in [
        ("Recipients",   "142",   "#1a0a00"),
        ("Opened",       "98 (69%)",  "#d4a017"),
        ("Clicked",      "41 (42%)",  "#8B4513"),
        ("Re-booked",    "12 (29%)",  "#28a745"),
        ("Avg Revenue",  "$524",  "#d4a017"),
    ]:
        st.markdown(f"""
        <div style="padding:10px 0;border-bottom:1px solid #f0e8dc">
          <div style="font-size:0.72rem;color:#888">{label}</div>
          <div style="font-size:1rem;font-weight:700;color:{color}">{val}</div>
        </div>
        """, unsafe_allow_html=True)
