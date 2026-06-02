import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import inject_css, page_header

st.set_page_config(page_title="Voice Agent — Velocity LA", page_icon="📞", layout="wide")
inject_css()
page_header("📞 Multilingual AI Voice Agent",
            "Answers inbound calls 24/7 · Books appointments · Speaks 12 languages")

# Auto-refresh every 5 seconds to animate the call timer
if st.session_state.get("_call_active"):
    st_autorefresh(interval=5000, key="voice_refresh")

# ── Layout ────────────────────────────────────────────────────────────────────
config_col, live_col = st.columns([1, 1], gap="large")

# ── LEFT: Configuration ────────────────────────────────────────────────────────
with config_col:
    st.markdown("#### Agent Configuration")
    st.markdown("""
    <div style="background:white;border:1px solid #e8dcc8;border-radius:10px;padding:20px 24px">
    """, unsafe_allow_html=True)

    st.selectbox("Language", [
        "English (US)", "Spanish", "Mandarin", "French",
        "Japanese", "Korean", "Portuguese", "Arabic",
    ])
    st.selectbox("Voice", ["Aria (Female)", "James (Male)", "Sofia (Female)", "Marcus (Male)"])
    st.selectbox("Knowledge Base", ["All Documents", "Pricing Only", "FAQ Only", "Booking Flow"])

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Today's stats
    st.markdown("#### Today's Call Stats")
    stats = [
        ("Total Calls", "24", "📞"),
        ("Answered",    "23 (96%)", "✅"),
        ("Avg Duration","04:32", "⏱️"),
        ("Booked",      "8", "📅"),
    ]
    for label, val, icon in stats:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
             padding:10px 0;border-bottom:1px solid #f0e8dc">
          <div style="font-size:0.82rem;color:#555">{icon} {label}</div>
          <div style="font-weight:700;color:#d4a017;font-size:0.9rem">{val}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Call log
    st.markdown("#### Recent Calls")
    calls = [
        ("+1 (310) 555-8765", "04:12", "Booked",        "#28a745"),
        ("+1 (213) 555-2340", "02:33", "Info Request",  "#d4a017"),
        ("+1 (424) 555-9012", "01:15", "Missed",        "#dc3545"),
        ("+1 (818) 555-4567", "05:44", "Booked",        "#28a745"),
        ("+1 (323) 555-7890", "03:08", "Callback Set",  "#8B4513"),
    ]
    for number, duration, outcome, color in calls:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:7px 0;
             border-bottom:1px solid #f0e8dc;font-size:0.78rem">
          <div style="color:#1a0a00;font-weight:600">{number}</div>
          <div style="color:#888">{duration}</div>
          <div><span style="background:{color};color:white;padding:1px 8px;
               border-radius:10px;font-size:0.68rem;font-weight:700">{outcome}</span></div>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT: Live call simulation ────────────────────────────────────────────────
with live_col:
    st.markdown("#### Live Call")

    call_active = st.session_state.get("_call_active", False)

    if not call_active:
        # Idle state
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);border-radius:14px;
             padding:40px 24px;text-align:center;min-height:320px;
             display:flex;flex-direction:column;justify-content:center;align-items:center">
          <div style="font-size:3rem;margin-bottom:12px">📞</div>
          <div style="font-weight:800;color:#d4a017;font-size:1.1rem;margin-bottom:6px">
            AI Voice Agent</div>
          <div style="color:rgba(255,255,255,0.65);font-size:0.85rem;margin-bottom:20px">
            Ready to answer calls 24/7<br>Powered by Vapi + ElevenLabs
          </div>
          <div style="background:#28a745;color:white;padding:4px 16px;border-radius:20px;
               font-size:0.8rem;font-weight:700">● ONLINE</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶  Simulate Inbound Call", type="primary", use_container_width=True):
            st.session_state._call_active = True
            st.session_state._call_tick = 0
            st.rerun()
    else:
        # Active call simulation
        tick = st.session_state.get("_call_tick", 0)
        st.session_state._call_tick = tick + 1
        total_secs = tick * 5
        mins = total_secs // 60
        secs = total_secs % 60
        timer = f"{mins:02d}:{secs:02d}"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a0a00,#3d1a00);border-radius:14px;
             padding:28px 24px;text-align:center">
          <div style="color:rgba(255,255,255,0.6);font-size:0.78rem;letter-spacing:1px;
               text-transform:uppercase;margin-bottom:12px">Speaking with</div>
          <div style="width:72px;height:72px;background:#d4a017;border-radius:50%;
               margin:0 auto 12px;display:flex;align-items:center;justify-content:center;
               font-size:2rem">👤</div>
          <div style="font-weight:800;color:white;font-size:1.1rem">Maria Garcia</div>
          <div style="color:rgba(255,255,255,0.6);font-size:0.8rem;margin-top:4px">
            +1 (310) 555-8765</div>
          <div style="font-size:2rem;font-weight:800;color:#d4a017;
               margin:16px 0;font-variant-numeric:tabular-nums">{timer}</div>
          <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;
               margin-bottom:20px">🎙 AI is speaking…</div>
        </div>
        """, unsafe_allow_html=True)

        # Call controls
        m1, m2, m3 = st.columns(3)
        with m1:
            st.button("🔇 Mute", use_container_width=True)
        with m2:
            st.button("⌨️ Keypad", use_container_width=True)
        with m3:
            if st.button("📵 End Call", use_container_width=True, type="primary"):
                st.session_state._call_active = False
                st.session_state._call_tick   = 0
                st.rerun()

        # Live transcript snippet
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Live Transcript**")
        script_lines = [
            ("Maya (AI)", "Thanks for calling Velocity LA! I'm Maya, your booking assistant. How can I help?"),
            ("Maria",     "Hi! I'm interested in driving a Lamborghini this Saturday."),
            ("Maya (AI)", "That's amazing — the Huracán has availability Saturday morning. Will it be just you or are you bringing anyone?"),
            ("Maria",     "Just me and my boyfriend, so two people."),
            ("Maya (AI)", "Perfect! And roughly what budget are you working with for the experience?"),
        ]
        display_count = min(tick + 1, len(script_lines))
        for speaker, line in script_lines[:display_count]:
            is_ai = "Maya" in speaker
            bg    = "#fdfaf5" if is_ai else "#f0f4ff"
            st.markdown(f"""
            <div style="background:{bg};border-radius:8px;padding:8px 12px;margin-bottom:6px">
              <div style="font-size:0.7rem;font-weight:700;color:#888;margin-bottom:2px">{speaker}</div>
              <div style="font-size:0.82rem;color:#1a0a00">{line}</div>
            </div>
            """, unsafe_allow_html=True)
