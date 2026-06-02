import streamlit as st

LUXURY_CSS = """
<style>
    .block-container { padding-top: 1.5rem; }

    .page-header {
        background: linear-gradient(135deg, #1a0a00 0%, #3d1a00 100%);
        color: white;
        padding: 22px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #d4a017;
    }
    .page-header h2 { margin: 0; font-size: 1.4rem; font-weight: 800; color: white; }
    .page-header p { margin: 5px 0 0; color: rgba(255,255,255,0.65); font-size: 0.85rem; }

    .lead-card {
        background: white;
        border: 1px solid #e8dcc8;
        border-radius: 8px;
        padding: 13px 15px;
        margin-bottom: 10px;
        border-left: 4px solid #d4a017;
    }
    .lead-card-name { font-weight: 700; color: #1a0a00; font-size: 0.92rem; }
    .lead-card-detail { font-size: 0.78rem; color: #666; margin-top: 2px; }

    .badge-hot {
        background: #d4a017; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.72rem; font-weight: 700;
    }
    .badge-warm {
        background: #8B4513; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.72rem; font-weight: 700;
    }
    .badge-cold {
        background: #999; color: white;
        padding: 2px 10px; border-radius: 12px;
        font-size: 0.72rem; font-weight: 700;
    }

    .metric-card {
        background: white;
        border: 1px solid #e8dcc8;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 800; color: #d4a017; line-height: 1.1; }
    .metric-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    .booking-confirm {
        background: linear-gradient(135deg, #1a0a00, #3d1a00);
        color: white;
        border-radius: 10px;
        padding: 28px;
        text-align: center;
        margin-top: 20px;
    }
    .booking-confirm h3 { color: #d4a017; margin: 0 0 8px; }
    .booking-confirm p { color: rgba(255,255,255,0.85); margin: 0; }
    .booking-confirm .sub { margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.18); font-size: 0.82rem; color: rgba(255,255,255,0.55); }
</style>
"""


def inject_css():
    st.markdown(LUXURY_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    inject_css()
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h2>{title}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def score_badge(score: float) -> str:
    if score >= 8:
        return f'<span class="badge-hot">🔥 HOT &nbsp;{score:.0f}/10</span>'
    if score >= 6:
        return f'<span class="badge-warm">⚡ WARM &nbsp;{score:.0f}/10</span>'
    if score > 0:
        return f'<span class="badge-cold">❄️ COLD &nbsp;{score:.0f}/10</span>'
    return '<span class="badge-cold">⬜ NEW</span>'


def metric_card(label: str, value: int, icon: str):
    st.markdown(
        f"""<div class="metric-card">
            <div style="font-size:1.5rem">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>""",
        unsafe_allow_html=True,
    )
