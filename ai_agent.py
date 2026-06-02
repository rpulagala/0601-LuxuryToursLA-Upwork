import json
import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
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

MODEL = "gemini-2.5-flash"


def _get_api_key() -> str:
    # .env locally → st.secrets on Streamlit Cloud
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    return key if key and key != "your-gemini-api-key-here" else ""


def _get_client():
    key = _get_api_key()
    return genai.Client(api_key=key) if key else None


def get_opening_message(first_name: str) -> str:
    fallback = (
        f"Hey {first_name}! Welcome to Velocity LA — "
        "which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"
    )
    client = _get_client()
    if not client:
        return fallback
    prompt = (
        f"You are Maya from Velocity LA luxury car experiences. "
        f"Write a warm, exciting opening SMS to {first_name} who just submitted a form. "
        f"Mention we have Lamborghini, Ferrari, McLaren, Porsche, and Rolls-Royce. "
        f"Ask which car interests them most. Under 30 words. No emojis."
    )
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception:
        return fallback


def get_ai_response(lead_id: int, user_message: str) -> tuple[str, dict | None]:
    """Return (response_text, qualification_dict_or_None)."""
    db = get_db()
    try:
        messages = (
            db.query(Conversation)
            .filter(Conversation.lead_id == lead_id)
            .order_by(Conversation.timestamp)
            .all()
        )
        history_lines = [
            f"{'Customer' if m.role == 'user' else 'Maya (you)'}: {m.message}"
            for m in messages
        ]
        history_text = "\n".join(history_lines)
    finally:
        db.close()

    def _scripted_fallback() -> str:
        asked = sum(1 for m in messages if m.role == "assistant")
        questions = [
            "Which car interests you most — Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?",
            "Great choice! What date or timeframe are you thinking for the experience?",
            "Perfect! How many people will be in your group?",
            "Awesome! And roughly what budget are you working with — under $500, $500-$1,000, or $1,000+?",
        ]
        return questions[asked] if asked < len(questions) else "You're all set! Let me grab a booking link for you."

    client = _get_client()
    if not client:
        return _scripted_fallback(), None

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"---\nCONVERSATION SO FAR:\n{history_text}\n\n"
        f"Customer: {user_message}\n\n"
        f"Your response as Maya (SMS style, max 2 sentences):"
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        response_text = response.text.strip()
    except Exception:
        return _scripted_fallback(), None

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
