import json
import os
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from database import get_db, Conversation

load_dotenv()

SYSTEM_PROMPT = """You are Maya, a friendly booking assistant for Velocity LA — a luxury exotic car driving experience company in Los Angeles.

Your goal is to qualify this lead by naturally collecting 4 pieces of information:
1. Which car they're interested in (Lamborghini Huracán, Ferrari 488 GTB, McLaren 720S, Porsche 911 GT3 RS, Rolls-Royce Ghost)
2. Their preferred date or timeframe (e.g. "this weekend", "mid-July", a specific date)
3. Group size — how many people total
4. Approximate budget (Under $500 / $500–$1,000 / $1,000+)

Rules:
- Maximum 2 sentences per message — this is SMS
- Ask only ONE question per message, never two
- Be warm, genuine, and enthusiastic — not salesy
- If they ask about pricing: "Experiences start from $399 per person — what budget range are you thinking?"
- If they seem ready to book: "Perfect! I can send you a booking link right now — want me to grab that for you?"
- Respond in whatever language the customer writes in

Once you have all 4 pieces of information, end your response with this exact line (no extra text after it):
QUALIFIED:{"car": "...", "date": "...", "group_size": "...", "budget": "...", "score": N}

Scoring guide — N should be an integer:
- Group 3+ AND budget $1,000+: score 9 or 10
- Solo/pair AND budget $500+: score 7 or 8
- Budget unclear or under $500: score 4 to 6"""


def _get_api_key() -> str:
    # .env locally → st.secrets on Streamlit Cloud
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    return key


def _get_model():
    api_key = _get_api_key()
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def get_opening_message(first_name: str) -> str:
    model = _get_model()
    fallback = (
        f"Hey {first_name}! 🏎️ Welcome to Velocity LA — "
        "which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"
    )
    if not model:
        return fallback
    prompt = (
        f"You are Maya from Velocity LA luxury car experiences. "
        f"Write a warm, exciting opening SMS to {first_name} who just submitted a form. "
        f"Mention we have Lamborghini, Ferrari, McLaren, Porsche, and Rolls-Royce. "
        f"Ask which car interests them most. Under 30 words. Start with one car emoji."
    )
    try:
        return model.generate_content(prompt).text.strip()
    except Exception:
        return fallback


def get_ai_response(lead_id: int, user_message: str) -> tuple[str, dict | None]:
    """Return (response_text, qualification_dict_or_None)."""
    model = _get_model()

    db = get_db()
    try:
        messages = (
            db.query(Conversation)
            .filter(Conversation.lead_id == lead_id)
            .order_by(Conversation.timestamp)
            .all()
        )
        history_lines = []
        for m in messages:
            speaker = "Customer" if m.role == "user" else "Maya (you)"
            history_lines.append(f"{speaker}: {m.message}")
        history_text = "\n".join(history_lines)
    finally:
        db.close()

    if not model:
        # Fallback: cycle through qualifying questions without AI
        fallback_questions = [
            "Which car interests you most — Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?",
            "Great choice! What date or timeframe are you thinking for the experience?",
            "Perfect! How many people will be in your group?",
            "Awesome! And roughly what budget are you working with — under $500, $500–$1,000, or $1,000+?",
        ]
        asked = sum(1 for m in messages if m.role == "assistant") if messages else 0
        if asked < len(fallback_questions):
            return fallback_questions[asked], None
        return "You're all set! Let me grab a booking link for you.", None

    prompt = f"""{SYSTEM_PROMPT}

---
CONVERSATION SO FAR:
{history_text}

Customer: {user_message}

Your response as Maya (SMS style, max 2 sentences):"""

    try:
        response_text = model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"Sorry, I'm having a moment — could you repeat that? (error: {e})", None

    qual_data = None
    if "QUALIFIED:" in response_text:
        match = re.search(r"QUALIFIED:\s*(\{.*?\})", response_text, re.DOTALL)
        if match:
            try:
                qual_data = json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        response_text = response_text[: response_text.index("QUALIFIED:")].strip()

    return response_text, qual_data
