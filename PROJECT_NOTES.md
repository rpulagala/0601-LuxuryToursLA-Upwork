# Velocity LA — AI Automation POC
## Project Notes & Build Log

---

## Overview

A Streamlit-based proof-of-concept demo for a luxury exotic car driving experience business in Los Angeles. Built to demonstrate the AI automation system proposed in the Upwork engagement before committing to the full GoHighLevel + Make + Vapi production build.

**Live demo:** `https://0601-luxurytoursla-upwork.streamlit.app`
**GitHub:** `https://github.com/rpulagala/0601-LuxuryToursLA-Upwork.git`
**Proposal file:** `Proposal_Luxury_Tour_AI_Automation.html`

---

## What the Demo Shows

Full customer journey from first lead touch to confirmed booking:

```
Lead Form → AI Qualification Chat → CRM Pipeline Dashboard → Booking Funnel
```

| Page | What it demonstrates |
|---|---|
| Landing page | Live metrics: total leads, qualified, booked, deposits |
| Lead Form | Website/Instagram embed simulation — creates a lead and fires AI opening message |
| AI Chat | Gemini AI qualifies lead via SMS-style conversation, scores 1–10, extracts car/date/group/budget |
| CRM Dashboard | Kanban pipeline (New Lead → Contacted → Qualified → Booked), nurture touch simulation, event log |
| Booking | Slot picker, car selector, mock deposit confirmation with balloons |

---

## Tech Stack

| Component | Tool | Notes |
|---|---|---|
| UI & routing | Streamlit | Multi-page via `pages/` directory |
| Database | SQLite + SQLAlchemy 2.0 | Ephemeral on Streamlit Cloud — auto-seeded on startup |
| AI agent | Google Gemini `gemini-2.5-flash` | Via `google-genai` SDK (new SDK, not deprecated `google-generativeai`) |
| Env config | `python-dotenv` | `.env` locally, `st.secrets` on Streamlit Cloud |
| Nurture sequence | APScheduler-free | 7-touch sequence triggered manually via dashboard button |

---

## File Structure

```
luxury-tour-poc/
├── streamlit_app.py          # Entry point — hero banner, live metrics, auto-seed on empty DB
├── pages/
│   ├── 1_Lead_Form.py        # Lead capture form
│   ├── 2_AI_Chat.py          # Gemini qualification chat
│   ├── 3_CRM_Dashboard.py    # Kanban + nurture simulation + Load/Reset buttons
│   └── 4_Booking.py          # Slot picker + mock checkout
├── database.py               # SQLAlchemy models: Lead, Conversation, Booking, NurtureEvent
├── ai_agent.py               # Gemini 2.5-flash integration, scoring, QUALIFIED JSON extraction
├── nurture.py                # 7-touch SMS/email sequence definitions
├── utils.py                  # Luxury CSS injection, score badges, metric cards
├── seed_data.py              # 100-lead seed script (also called on startup if DB empty)
├── requirements.txt
├── .gitignore                # Excludes .env, secrets.toml, leads.db
├── .streamlit/
│   ├── config.toml           # Gold/brown luxury theme
│   └── secrets.toml.example  # Template — copy and fill with real key
└── CLAUDE.md                 # Claude Code instructions for this repo
```

---

## Database Models

```
Lead              — name, email, phone, source, preferred_car, preferred_date,
                    group_size, budget, score (float), pipeline_stage, tag, created_at

Conversation      — lead_id (FK), role (user/assistant), message, timestamp

Booking           — lead_id (FK), slot_date, slot_time, car, amount, confirmed_at

NurtureEvent      — lead_id (FK), touch_number, channel, subject, message, sent_at
```

**Pipeline stages:** `New Lead` → `Contacted` → `Qualified` → `Booked`

**Tags:** `New` / `Hot` (score ≥ 8) / `Warm` (score 6–7) / `Cold` (score < 6)

---

## AI Agent Logic (`ai_agent.py`)

- **SDK:** `google-genai` (new, not deprecated `google-generativeai`)
- **Model:** `gemini-2.5-flash`
- **Key loading:** `os.getenv("GEMINI_API_KEY")` from `.env` → falls back to `st.secrets`
- **Prompt strategy:** Full conversation history passed as text in a single `generate_content` call (no Chat API — more reliable across sessions)
- **Qualification trigger:** When all 4 fields collected, model appends `QUALIFIED:{...json...}` to its response; `ai_agent.py` strips it, parses the JSON, updates the Lead record
- **Graceful fallback:** If the API call fails for any reason (quota, bad key, network), silently falls back to 4 scripted qualifying questions — demo still works end-to-end

**Scoring guide in system prompt:**
- Group 3+ AND budget $1,000+: score 9–10
- Solo/pair AND budget $500+: score 7–8
- Budget unclear or under $500: score 4–6

---

## Seed Data (`seed_data.py`)

100 leads generated with `random.seed(42)` for reproducibility:

| Stage | Count | Score range | Notes |
|---|---|---|---|
| Booked | 8 | 8–10 | Full conversations + booking records |
| Qualified Hot | 22 | 8–10 | Full conversations |
| Qualified Warm | 20 | 6–7 | Full conversations |
| Contacted | 30 | 0 | Partial convos + 0–4 nurture touches each |
| New Lead | 20 | 0 | Opening message only |

**Totals:** 100 leads, 8 bookings, ~620 conversations, ~61 nurture events

**Auto-seed logic:** `streamlit_app.py` checks `Lead.count() == 0` on startup and calls `seed()` if true. This handles Streamlit Cloud's ephemeral filesystem — data reappears after every container restart without manual action.

---

## Nurture Sequence

7 touches defined in `nurture.py`, triggered manually via the 📨 button per lead in the dashboard:

| Touch | Channel | Subject |
|---|---|---|
| 1 | SMS | Checking in |
| 2 | Email | What our guests say |
| 3 | SMS | What's holding you back? |
| 4 | Email | FAQ before your first drive |
| 5 | SMS | Slots filling up |
| 6 | Email | Is it the price? |
| 7 | SMS | Last chance |

---

## Setup — Local

```bash
# 1. Clone
git clone https://github.com/rpulagala/0601-LuxuryToursLA-Upwork.git
cd 0601-LuxuryToursLA-Upwork

# 2. Install
pip install -r requirements.txt

# 3. Add API key
# Create .env in the project root:
echo "GEMINI_API_KEY=your-key-here" > .env

# 4. Run
streamlit run streamlit_app.py
# Opens at http://localhost:8501
# DB auto-seeds with 100 leads on first run
```

---

## Setup — Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → New app
2. Repo: `rpulagala/0601-LuxuryToursLA-Upwork` · Branch: `main` · File: `streamlit_app.py`
3. Advanced settings → Secrets:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Deploy — app auto-seeds 100 leads on first load

---

## Issues Encountered & Fixes

### SQLAlchemy 2.0 — `bind=` removed
Streamlit Cloud installs SQLAlchemy 2.x. The `bind=` keyword was removed from both `sessionmaker()` and `create_all()`.
- **Fix:** `sessionmaker(engine)` and `create_all(engine)` (no `bind=` kwarg)
- **Also fixed:** `os.path.abspath(__file__)` for reliable DB path resolution on cloud

### `google.generativeai` deprecated
The entire `google-generativeai` package has been deprecated. All support ended.
- **Fix:** Migrated to `google-genai` SDK
  - Old: `import google.generativeai as genai` / `genai.configure(api_key=...)` / `genai.GenerativeModel(...)`
  - New: `from google import genai` / `genai.Client(api_key=...)` / `client.models.generate_content(...)`

### `gemini-1.5-flash` not available → `gemini-2.0-flash` retired
- `gemini-1.5-flash` — not available for this key type
- `gemini-2.0-flash` — retired after initial migration
- **Fix:** `gemini-2.5-flash` — confirmed working

### Free-tier quota exhausted
Key format `AQ.Ab8RN6KJ-...` is a paid-tier key with free-tier quota explicitly set to 0.
- **Fix:** Added $10 credit to Google AI account — API now fully active

### Blank dashboard on Streamlit Cloud
SQLite DB is ephemeral — wiped on every container restart.
- **Fix:** Auto-seed check in `streamlit_app.py` on every startup

### Windows console `UnicodeEncodeError`
Emoji characters in `print()` statements crash on Windows `cp1252` terminal.
- **Fix:** Removed emoji from print statements in `seed_data.py`

---

## API Key Notes

- Key: stored in `.env` (local) and Streamlit Cloud Secrets dashboard (do not commit)
- Format: Paid-tier Google AI Studio key (not `AIza...` format — this is newer)
- Credit: $10 added June 2026
- Model in use: `gemini-2.5-flash`
- Estimated cost per qualification conversation (~8 messages): < $0.01

---

## Production Build Mapping

This POC demonstrates the same concepts as the full GoHighLevel production system:

| POC (this app) | Production (GoHighLevel build) |
|---|---|
| Streamlit form | GHL funnel + Instagram/TikTok lead ads |
| SQLite pipeline | GHL CRM + pipeline stages |
| Gemini AI chat | GPT-4o/Claude via Make webhook + GHL SMS |
| Manual nurture buttons | GHL automated workflow sequences |
| Mock booking | GHL Calendar + Stripe deposit |
| No waiver/docs | PandaDoc waiver + AWS S3 document vault (Phase 2) |
| No voice agent | Vapi + ElevenLabs multilingual agent (Phase 4) |

---

## Commit History

| Commit | Change |
|---|---|
| `0d8f447` | Initial commit — full POC build |
| `f252c58` | Fix SQLAlchemy 2.0 `bind=` compatibility |
| `dafc42f` | Add 100-lead seed script + Load Sample Data button |
| `cada690` | Migrate to google-genai SDK, add graceful fallback |
| `28b4bea` | Expand to 100 leads, auto-seed on startup |
| `ed18639` | Update model to gemini-2.5-flash |

---

*Built June 2026 · Ravi Pulagala · rpulagala@gmail.com*
