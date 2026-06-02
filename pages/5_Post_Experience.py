import streamlit as st
from utils import inject_css, page_header

st.set_page_config(page_title="Post-Experience — Velocity LA", page_icon="⭐", layout="wide")
inject_css()
page_header("⭐ Post Experience Automation", "Reviews & Referrals workflow — triggers automatically after each booking")

# ── Workflow status toggle ────────────────────────────────────────────────────
c1, c2 = st.columns([5, 1])
with c2:
    active = st.toggle("Active", value=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Workflow stats ─────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
for col, label, val, sub in [
    (s1, "Enrolled",         "128", "all time"),
    (s2, "Completed",        "128", "100%"),
    (s3, "Reviews Received", "89",  "69.5% rate"),
    (s4, "Last 7 Days",      "34",  "new reviews"),
]:
    col.markdown(f"""
    <div style="background:white;border:1px solid #e8dcc8;border-radius:8px;
         padding:16px;text-align:center">
      <div style="font-size:1.8rem;font-weight:800;color:#d4a017">{val}</div>
      <div style="font-size:0.78rem;font-weight:700;color:#1a0a00;margin-top:4px">{label}</div>
      <div style="font-size:0.72rem;color:#888">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Workflow diagram ───────────────────────────────────────────────────────────
st.markdown("#### Automated Workflow")

def workflow_node(icon, title, subtitle, color="#d4a017"):
    return f"""
    <div style="background:white;border:2px solid {color};border-radius:10px;
         padding:12px 14px;text-align:center;min-height:80px;
         display:flex;flex-direction:column;justify-content:center">
      <div style="font-size:1.4rem">{icon}</div>
      <div style="font-weight:700;color:#1a0a00;font-size:0.82rem;margin-top:4px">{title}</div>
      <div style="font-size:0.7rem;color:#888;margin-top:2px">{subtitle}</div>
    </div>"""

def arrow():
    return """<div style="text-align:center;font-size:1.3rem;color:#d4a017;
              padding:4px 0">→</div>"""

# Row 1: trigger → wait → review request
r1 = st.columns([3, 1, 3, 1, 3, 1, 3])
r1[0].markdown(workflow_node("🏎️", "Experience Complete", "Booking marked done"), unsafe_allow_html=True)
r1[1].markdown(arrow(), unsafe_allow_html=True)
r1[2].markdown(workflow_node("⏱️", "Wait 2 Hours", "Post-experience cool-down"), unsafe_allow_html=True)
r1[3].markdown(arrow(), unsafe_allow_html=True)
r1[4].markdown(workflow_node("📱", "Send SMS", "\"How was your drive?\""), unsafe_allow_html=True)
r1[5].markdown(arrow(), unsafe_allow_html=True)
r1[6].markdown(workflow_node("📧", "Send Review Email", "Yelp · Google · TripAdvisor"), unsafe_allow_html=True)

st.markdown("<div style='text-align:center;font-size:1.3rem;color:#d4a017;padding:4px 0'>↓</div>", unsafe_allow_html=True)

# Row 2: split by response
r2 = st.columns([2, 1, 2, 1, 2])
r2[0].markdown(workflow_node("⭐", "Review Posted", "Link opens → review submitted", "#28a745"), unsafe_allow_html=True)
r2[1].markdown("<div style='padding-top:30px;text-align:center;color:#ccc'>or</div>", unsafe_allow_html=True)
r2[2].markdown(workflow_node("⏭️", "No Response", "Wait 3 days then follow up", "#8B4513"), unsafe_allow_html=True)
r2[3].markdown(arrow(), unsafe_allow_html=True)
r2[4].markdown(workflow_node("🎁", "Referral Offer", "20% off for a friend", "#d4a017"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Review platform breakdown ─────────────────────────────────────────────────
st.markdown("#### Review Platform Breakdown")
p1, p2, p3, p4 = st.columns(4)
for col, platform, count, color in [
    (p1, "⭐ Google",      "41", "#4285F4"),
    (p2, "🔴 Yelp",        "28", "#d32323"),
    (p3, "✈️ TripAdvisor", "15", "#00AF87"),
    (p4, "📘 Facebook",    "5",  "#1877F2"),
]:
    col.markdown(f"""
    <div style="background:white;border:1px solid #e8dcc8;border-radius:8px;
         padding:14px;text-align:center;border-top:3px solid {color}">
      <div style="font-size:1.5rem;font-weight:800;color:{color}">{count}</div>
      <div style="font-size:0.8rem;color:#444;margin-top:3px">{platform}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sample review ──────────────────────────────────────────────────────────────
st.markdown("#### Sample Generated Review Request")
st.markdown("""
<div style="background:#fdfaf5;border:1px solid #e8dcc8;border-radius:10px;padding:20px 24px;
     max-width:480px">
  <div style="display:flex;justify-content:space-between;margin-bottom:10px">
    <div style="font-weight:700;color:#1a0a00;font-size:0.9rem">📱 SMS — 2 hrs after experience</div>
    <div style="font-size:0.72rem;color:#888">Auto-sent</div>
  </div>
  <div style="background:white;border-radius:12px 12px 12px 0;padding:12px 14px;
       border:1px solid #e8dcc8;font-size:0.85rem;color:#333;line-height:1.6">
    Hey Marcus! 🏎️ Hope you loved the Lamborghini Huracán experience today!
    We'd love to hear your thoughts — it only takes 60 seconds:<br><br>
    <strong style="color:#4285F4">⭐ Leave a Google Review →</strong><br><br>
    Your feedback means the world to us. — Maya, Velocity LA
  </div>
  <div style="margin-top:10px;font-size:0.72rem;color:#888">
    AI-personalized · Sent automatically · No manual work required
  </div>
</div>
""", unsafe_allow_html=True)
