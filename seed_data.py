"""
Run once to populate the demo database with realistic sample data.
    python seed_data.py
"""
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Conversation, Booking, NurtureEvent

def seed():
    init_db()
    db = get_db()
    try:
        # ── Wipe existing data ────────────────────────────────────────────────
        db.query(NurtureEvent).delete()
        db.query(Conversation).delete()
        db.query(Booking).delete()
        db.query(Lead).delete()
        db.commit()

        now = datetime.utcnow()

        # ── Lead 1: BOOKED — Priya Patel ──────────────────────────────────────
        priya = Lead(
            name="Priya Patel",
            email="priya.patel@gmail.com",
            phone="+1 (310) 482-9901",
            source="Instagram",
            preferred_car="Lamborghini Huracán",
            preferred_date="Saturday, Jul 12",
            group_size="2",
            budget="$1,000+",
            score=9.0,
            pipeline_stage="Booked",
            tag="Hot",
            created_at=now - timedelta(hours=5),
        )
        db.add(priya)
        db.flush()

        for role, msg, offset in [
            ("assistant", "Hey Priya! 🏎️ Welcome to Velocity LA — which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?", 300),
            ("user",      "Hi! I've always wanted to drive a Lamborghini!", 240),
            ("assistant", "Amazing choice — the Huracán is pure adrenaline on LA roads! Do you have a date in mind, or are you flexible?", 180),
            ("user",      "I was thinking this Saturday, July 12th", 150),
            ("assistant", "Saturday the 12th works perfectly — we have morning and afternoon slots available. Will it just be you, or are you bringing someone along?", 120),
            ("user",      "My boyfriend is coming too, so just 2 of us", 90),
            ("assistant", "Perfect — a private experience for two is honestly the best way to do it. Just so I can confirm the right package, what budget range are you working with?", 60),
            ("user",      "We're happy to spend over $1000 for the right experience", 30),
            ("assistant", "You're all set, Priya! 🎉 Your Lamborghini Huracán experience is confirmed for Saturday, Jul 12 at 11:00 AM. We'll send a reminder 48 hours before. See you on the road!", 5),
        ]:
            db.add(Conversation(lead_id=priya.id, role=role, message=msg,
                                timestamp=now - timedelta(minutes=offset)))

        db.add(Booking(
            lead_id=priya.id,
            slot_date="Saturday, Jul 12",
            slot_time="11:00 AM",
            car="Lamborghini Huracán",
            amount="$599",
            confirmed_at=now - timedelta(hours=4),
        ))

        # ── Lead 2: QUALIFIED HOT — Marcus Chen ───────────────────────────────
        marcus = Lead(
            name="Marcus Chen",
            email="marcus.chen@outlook.com",
            phone="+1 (424) 317-5522",
            source="TikTok",
            preferred_car="McLaren 720S",
            preferred_date="Weekend of July 19",
            group_size="4",
            budget="$1,000+",
            score=10.0,
            pipeline_stage="Qualified",
            tag="Hot",
            created_at=now - timedelta(hours=3),
        )
        db.add(marcus)
        db.flush()

        for role, msg, offset in [
            ("assistant", "Hey Marcus! 🏎️ Thanks for reaching out to Velocity LA — which exotic car caught your eye: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?", 160),
            ("user",      "McLaren 720S without a doubt. Saw it on your TikTok and I was sold immediately", 140),
            ("assistant", "The 720S is an absolute beast — great taste. When are you thinking of coming in?", 120),
            ("user",      "Weekend of the 19th ideally, maybe Saturday or Sunday", 100),
            ("assistant", "Both days look good right now. How many people are you bringing?", 80),
            ("user",      "4 of us total — it's kind of a birthday thing for my friend", 60),
            ("assistant", "That sounds incredible — a birthday in a McLaren is unforgettable. What budget range works for the group?", 40),
            ("user",      "Money isn't really an issue, we want the full experience. Easily $1000+ per person", 20),
            ("assistant", "Perfect — a group of 4 with no budget ceiling is exactly what we love to work with. Let me get you a booking link right now!", 5),
        ]:
            db.add(Conversation(lead_id=marcus.id, role=role, message=msg,
                                timestamp=now - timedelta(minutes=offset)))

        # ── Lead 3: QUALIFIED WARM — Sofia Rodriguez ──────────────────────────
        sofia = Lead(
            name="Sofia Rodriguez",
            email="sofiar@gmail.com",
            phone="+1 (213) 904-7731",
            source="Google Ads",
            preferred_car="Ferrari 488 GTB",
            preferred_date="Late July",
            group_size="1",
            budget="$500–$1,000",
            score=7.0,
            pipeline_stage="Qualified",
            tag="Warm",
            created_at=now - timedelta(hours=7),
        )
        db.add(sofia)
        db.flush()

        for role, msg, offset in [
            ("assistant", "Hi Sofia! 🏎️ Welcome to Velocity LA — which car are you most excited to drive: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?", 200),
            ("user",      "Ferrari for sure, always been a dream of mine", 180),
            ("assistant", "The 488 GTB will absolutely deliver that dream — it sounds incredible. Do you have a timeframe in mind?", 160),
            ("user",      "Sometime in late July works for me", 130),
            ("assistant", "Late July is a great time — we have availability. Will it be just you or is someone joining?", 100),
            ("user",      "Just me, solo experience", 80),
            ("assistant", "Solo is a great way to fully focus on the car. Roughly what budget are you working with for the experience?", 55),
            ("user",      "Probably between $500 and $1000", 30),
            ("assistant", "That works perfectly for our Ferrari package — you'll be in great shape. Ready to lock in a date?", 5),
        ]:
            db.add(Conversation(lead_id=sofia.id, role=role, message=msg,
                                timestamp=now - timedelta(minutes=offset)))

        # ── Lead 4: CONTACTED COLD — James Walker ─────────────────────────────
        james = Lead(
            name="James Walker",
            email="jwalker88@yahoo.com",
            phone="+1 (818) 223-6614",
            source="Website",
            preferred_car="Porsche 911 GT3 RS",
            preferred_date="",
            group_size="",
            budget="",
            score=0.0,
            pipeline_stage="Contacted",
            tag="New",
            created_at=now - timedelta(hours=12),
        )
        db.add(james)
        db.flush()

        for role, msg, offset in [
            ("assistant", "Hey James! 🏎️ Welcome to Velocity LA — which car are you most excited about: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?", 700),
            ("user",      "Porsche GT3 RS", 650),
            ("assistant", "Excellent choice — the GT3 RS is pure driver's car. Do you have a date in mind, or are you still exploring?", 600),
            ("user",      "Just exploring for now, not sure on timing yet", 550),
            ("assistant", "No rush at all — whenever you're ready I can check availability. Just reply here and I'll get you sorted! 🙌", 500),
        ]:
            db.add(Conversation(lead_id=james.id, role=role, message=msg,
                                timestamp=now - timedelta(minutes=offset)))

        # 2 nurture touches already sent to James
        for touch_num, channel, subject, msg_body, offset_hrs in [
            (1, "SMS",   "Checking in",
             "Hey James! Just checking in — did you get a chance to think about which experience you'd like? Our Porsche slots this weekend are filling up fast. 🏎️",
             10),
            (2, "Email", "What our guests say",
             "Hi James,\n\nWe wanted to share what a recent guest said:\n\n\"I've driven sports cars before but the Porsche GT3 RS on the open road around LA was a completely different level. Worth every penny.\"\n\nWhenever you're ready, I'm here to help you book.\n\nMaya | Velocity LA",
             6),
        ]:
            db.add(NurtureEvent(
                lead_id=james.id,
                touch_number=touch_num,
                channel=channel,
                subject=subject,
                message=msg_body,
                sent_at=now - timedelta(hours=offset_hrs),
            ))

        # ── Lead 5: NEW LEAD — Ashley Kim ─────────────────────────────────────
        ashley = Lead(
            name="Ashley Kim",
            email="ashleyk@icloud.com",
            phone="+1 (323) 771-4480",
            source="Friend / Referral",
            preferred_car="Rolls-Royce Ghost",
            preferred_date="",
            group_size="",
            budget="",
            score=0.0,
            pipeline_stage="Contacted",
            tag="New",
            created_at=now - timedelta(minutes=8),
        )
        db.add(ashley)
        db.flush()

        db.add(Conversation(
            lead_id=ashley.id,
            role="assistant",
            message="Hey Ashley! 👋 Welcome to Velocity LA — which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?",
            timestamp=now - timedelta(minutes=6),
        ))

        db.commit()
        print("Sample data loaded successfully.")
        print("  Booked:    Priya Patel (Lamborghini Huracán)")
        print("  Hot:       Marcus Chen (McLaren 720S - score 10)")
        print("  Warm:      Sofia Rodriguez (Ferrari 488 GTB - score 7)")
        print("  Contacted: James Walker (Porsche GT3 RS - 2 nurture touches sent)")
        print("  New:       Ashley Kim (Rolls-Royce Ghost - awaiting reply)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
