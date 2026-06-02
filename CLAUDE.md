# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **proposal repository** for a Luxury Tour & Exotic Car AI Automation project (Upwork engagement). It contains no application code, backend, or build system — only the client-facing proposal and project context.

| File | Purpose |
|---|---|
| `Proposal_Luxury_Tour_AI_Automation.html` | Standalone HTML proposal delivered to the client |
| `project_luxury_tour_ai_automation_memory.md` | Internal project context: tech stack, phases, budget, pre-start questions |

## Viewing the Proposal

Open `Proposal_Luxury_Tour_AI_Automation.html` directly in any browser — it is a self-contained file with no external dependencies or build step required.

## Proposal Design Conventions

- **Color palette:** dark brown (`#1a0a00`, `#3d1a00`) + gold (`#d4a017`) on white — luxury aesthetic
- **Typography:** Segoe UI at 15px base, 1.7 line-height
- **Layout:** Single `.page` container (max 880px), CSS Grid for cards, no JS
- **Sections follow a fixed order:** cover → overview → architecture → tech stack → phases → timeline → budget → experience cards → questions → closing → footer
- **Phase blocks** use `.phase-block` + `.phase-header` + `.phase-body` structure; each phase has a `.deliverables` callout
- **Responsive breakpoint** at 640px collapses card grids to single column

## Project Context

- **Client:** Luxury tour & exotic car driving experience business, Los Angeles
- **Proposed stack:** GoHighLevel (CRM hub) + Make/n8n (automations) + OpenAI GPT-4o / Claude (AI conversations) + Vapi + ElevenLabs (voice agent) + PandaDoc/DocuSign (waivers) + AWS S3 (document vault) + Stripe (payments) + Airtable (reporting)
- **Budget:** $9,200–$12,300 one-time build; ~$435–$680/mo ongoing platform costs (paid by client)
- **Timeline:** 14 weeks across 4 phases
- **Status as of June 2026:** Proposal submitted, awaiting client response
