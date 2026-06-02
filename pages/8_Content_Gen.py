import streamlit as st
import os
from dotenv import load_dotenv
from utils import inject_css, page_header

st.set_page_config(page_title="Content Generator — Velocity LA", page_icon="✨", layout="wide")
inject_css()
page_header("✨ AI Content Generation Assistant",
            "Turn experience descriptions into platform-ready social media posts")

load_dotenv()

PLATFORMS = {
    "TikTok":    {"icon": "🎵", "limit": 150,  "style": "punchy, Gen-Z energy, 3-5 short sentences, hype language"},
    "Instagram": {"icon": "📸", "limit": 200,  "style": "aspirational and visual, storytelling tone, lifestyle focus"},
    "YouTube":   {"icon": "▶️", "limit": 300,  "style": "SEO-optimized description, keyword-rich, call to subscribe"},
    "Facebook":  {"icon": "📘", "limit": 250,  "style": "conversational and friendly, slightly longer, community feel"},
    "Twitter/X": {"icon": "𝕏",  "limit": 280,  "style": "witty, short punchy statement, max 280 chars total"},
}

def _get_client():
    try:
        from google import genai
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            try:
                key = st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                pass
        return genai.Client(api_key=key) if key and key != "your-gemini-api-key-here" else None
    except Exception:
        return None


def generate_content(platform: str, description: str, car: str) -> str:
    p = PLATFORMS[platform]
    client = _get_client()
    if not client:
        # Fallback copy
        return (
            f"Feel the power. Live the dream. Drive iconic. Drive unforgettable.\n\n"
            f"Only in Los Angeles — {car} experience, now available.\n\n"
            f"#ExoticCars #LuxuryDriving #LosAngeles #VelocityLA #{car.split()[0]}"
        )
    prompt = (
        f"You are a luxury car experience social media copywriter for Velocity LA in Los Angeles.\n"
        f"Platform: {platform} ({p['style']})\n"
        f"Car featured: {car}\n"
        f"Experience description: {description}\n\n"
        f"Write a caption under {p['limit']} words. Include 5-8 relevant hashtags at the end.\n"
        f"Do NOT include the platform name in the output. Just the caption and hashtags."
    )
    try:
        from google.genai import types
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.85),
        )
        return response.text.strip()
    except Exception as e:
        return f"(API error — check GEMINI_API_KEY)\n\n{e}"


# ── Layout ────────────────────────────────────────────────────────────────────
input_col, output_col = st.columns([1, 2], gap="large")

with input_col:
    st.markdown("#### Experience Input")

    car = st.selectbox("Car Featured", [
        "Lamborghini Huracán", "Ferrari 488 GTB",
        "McLaren 720S", "Porsche 911 GT3 RS", "Rolls-Royce Ghost",
    ])

    description = st.text_area(
        "Description / Voice Transcript",
        placeholder=(
            "Paste a voice note transcript or write a short description of the experience.\n\n"
            "Example: Marcus drove the Lamborghini Huracán through Malibu Canyon today — "
            "said it was the best 90 minutes of his life. Group of 3, all first-timers."
        ),
        height=200,
    )

    selected_platforms = st.multiselect(
        "Platforms",
        list(PLATFORMS.keys()),
        default=["Instagram", "TikTok"],
    )

    generate_clicked = st.button(
        "✨ Generate Content",
        type="primary",
        use_container_width=True,
        disabled=not description.strip() or not selected_platforms,
    )

    if generate_clicked and description.strip():
        st.session_state._gen_results = {}
        for platform in selected_platforms:
            with st.spinner(f"Writing {platform} caption…"):
                st.session_state._gen_results[platform] = generate_content(
                    platform, description.strip(), car
                )
        st.rerun()

    # Example prompts
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Quick Examples**")
    examples = [
        "Client drove the Ferrari 488 GTB through the Hollywood Hills. Solo trip, 90 mins, said it exceeded every expectation.",
        "Group of 4 friends rented the McLaren 720S for a birthday. Took coastal route through Pacific Palisades. Everyone was speechless.",
    ]
    for ex in examples:
        if st.button(f"💬 {ex[:55]}…", use_container_width=True):
            st.session_state._example_desc = ex
            st.rerun()

    if "example_desc" in st.session_state:
        description = st.session_state.pop("_example_desc")

with output_col:
    st.markdown("#### Generated Content")

    results = st.session_state.get("_gen_results", {})

    if not results:
        st.markdown("""
        <div style="background:white;border:1px dashed #e8dcc8;border-radius:12px;
             padding:48px 24px;text-align:center;color:#aaa">
          <div style="font-size:2.5rem;margin-bottom:12px">✨</div>
          <div style="font-size:0.9rem">
            Select platforms, paste a description, and hit Generate.<br>
            AI will write platform-native captions in seconds.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for platform, content in results.items():
            p = PLATFORMS[platform]
            st.markdown(f"""
            <div style="background:white;border:1px solid #e8dcc8;border-radius:10px;
                 padding:16px 18px;margin-bottom:12px;border-top:3px solid #d4a017">
              <div style="font-weight:700;color:#1a0a00;font-size:0.9rem;margin-bottom:8px">
                {p['icon']} {platform}
              </div>
            """, unsafe_allow_html=True)

            edited = st.text_area(
                f"Caption", value=content, height=140,
                key=f"edit_{platform}", label_visibility="collapsed",
            )

            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("📋 Copy", key=f"copy_{platform}", use_container_width=True):
                    st.toast(f"{platform} caption copied!")
            with btn2:
                if st.button("🔁 Regenerate", key=f"regen_{platform}", use_container_width=True):
                    with st.spinner("Rewriting…"):
                        st.session_state._gen_results[platform] = generate_content(
                            platform, description, car
                        )
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # Schedule button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📅 Schedule All Posts", type="primary", use_container_width=True):
            st.success("Posts scheduled via GoHighLevel Social Planner. (Demo — no actual post sent.)")
