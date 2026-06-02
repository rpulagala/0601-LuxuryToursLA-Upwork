# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A **client demo app** for a Luxury Tour & Exotic Car AI Automation pitch (Upwork engagement). It contains:

- A live Streamlit demo app ("Velocity LA") showing an AI-powered customer journey
- `Proposal_Luxury_Tour_AI_Automation.html` — standalone client-facing proposal
- `project_luxury_tour_ai_automation_memory.md` — internal project context

## Running the App

```
streamlit run streamlit_app.py
```

**API key setup (required for live AI):**
- Local: copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill in `GEMINI_API_KEY`
- Alternatively set `GEMINI_API_KEY` in a `.env` file
- Streamlit Cloud: set `GEMINI_API_KEY` in the app's Secrets settings
- Without a key the app falls back to a scripted response sequence (no error thrown)

## App Architecture

**Entry point:** `streamlit_app.py` — initializes DB, auto-seeds 100 leads if the DB is empty, renders the hero dashboard with live pipeline metrics.

**Four Streamlit pages** (sidebar navigation in order):
1. `pages/1_Lead_Form.py` — captures a prospect; creates a `Lead` row and triggers AI opening message
2. `pages/2_AI_Chat.py` — SMS-style chat with Maya (AI agent); parses `QUALIFIED:{...}` signal from model to update lead score and pipeline stage
3. `pages/3_CRM_Dashboard.py` — Kanban pipeline board; lets user simulate nurture touches (email/SMS sequence)
4. `pages/4_Booking.py` — booking slot picker for qualified leads; creates a `Booking` row and marks lead as Booked

**Modules:**
- `database.py` — SQLAlchemy models (`Lead`, `Conversation`, `Booking`, `NurtureEvent`) on SQLite (`leads.db`); `init_db()` / `get_db()` helpers
- `ai_agent.py` — Google Gemini 2.5 Flash integration; `get_opening_message()` and `get_ai_response()`; graceful scripted fallback when no API key; parses structured `QUALIFIED:{json}` signal from model output
- `nurture.py` — 7-touch nurture sequence (alternating SMS/Email); `get_next_touch()` / `log_nurture_event()`
- `utils.py` — shared CSS (`LUXURY_CSS`), `inject_css()`, `page_header()`, `score_badge()`, `metric_card()`
- `seed_data.py` — generates 100 synthetic leads with realistic spread across pipeline stages

**Data flow:** Lead Form → `Lead` row created (stage: Contacted) → AI Chat qualifies → score + stage updated (stage: Qualified) → Booking page → `Booking` row created (stage: Booked). Nurture events are logged to `NurtureEvent` and displayed in the CRM dashboard activity feed.

**AI qualification signal:** When the model has collected car, date, group size, and budget, it appends `QUALIFIED:{"car":"...","date":"...","group_size":"...","budget":"...","score":N}` to its response. `ai_agent.py` strips this before displaying and uses it to update the lead record.

## Key Design Decisions

- `leads.db` is local SQLite; ephemeral on Streamlit Cloud — auto-seed on startup handles this
- `get_db()` returns a raw session (not a context manager); callers must close it in a `try/finally`
- No real SMS/email is sent — all nurture touches are simulated and logged to DB only
- Score thresholds: ≥8 = HOT (gold badge), ≥6 = WARM, >0 = COLD, 0 = NEW

## Proposal Design Conventions

The `Proposal_Luxury_Tour_AI_Automation.html` is a self-contained file (no build step, no external deps).

- **Color palette:** dark brown (`#1a0a00`, `#3d1a00`) + gold (`#d4a017`) — matches the app's CSS
- **Section order:** cover → overview → architecture → tech stack → phases → timeline → budget → experience cards → questions → closing → footer
- **Phase blocks** use `.phase-block` + `.phase-header` + `.phase-body`; each phase has a `.deliverables` callout
- **Responsive breakpoint** at 640px collapses card grids to single column
