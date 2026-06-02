from database import get_db, NurtureEvent, Lead

NURTURE_SEQUENCE = [
    {
        "touch": 1,
        "channel": "SMS",
        "subject": "Checking in",
        "message": "Hey {name}! Just checking in — did you get a chance to think about which experience you'd like? Our Lamborghini slots this weekend are filling up fast. 🏎️",
    },
    {
        "touch": 2,
        "channel": "Email",
        "subject": "What our guests say",
        "message": (
            "Hi {name},\n\n"
            "We wanted to share what a recent guest said:\n\n"
            "\"I've driven sports cars before but the Lamborghini Huracán on the open road around LA was a completely different level. Worth every penny.\"\n\n"
            "Whenever you're ready, I'm here to help you book. Just reply to this email.\n\n"
            "Maya | Velocity LA"
        ),
    },
    {
        "touch": 3,
        "channel": "SMS",
        "subject": "What's holding you back?",
        "message": "Hi {name}, quick question — is it the price, the timing, or something else holding you back? No pressure, just want to make sure I can help. 🙏",
    },
    {
        "touch": 4,
        "channel": "Email",
        "subject": "FAQ — Before your first Velocity LA experience",
        "message": (
            "Hi {name},\n\n"
            "Top questions we get:\n\n"
            "✅ Do I need a racing license? No — just a valid driver's license.\n"
            "✅ How long is the experience? 60–90 minutes on average.\n"
            "✅ Can friends come and watch? Absolutely.\n"
            "✅ Never driven a supercar? Our team guides you the whole way.\n\n"
            "Ready to book? Just reply!\n\nMaya | Velocity LA"
        ),
    },
    {
        "touch": 5,
        "channel": "SMS",
        "subject": "Slots filling up",
        "message": "Hi {name}, July slots are getting booked up — wanted to give you a heads-up before we're fully sold out. Want me to hold a spot? 📅",
    },
    {
        "touch": 6,
        "channel": "Email",
        "subject": "Is it the price?",
        "message": (
            "Hi {name},\n\n"
            "I want to be upfront — our experiences aren't cheap. But here's what you're actually getting:\n\n"
            "• A real supercar, not a track rental\n"
            "• A private experience — no strangers in your group\n"
            "• Professional photography included\n"
            "• Routes through iconic LA scenery\n\n"
            "Most guests say it's the best $500 they've ever spent. We also offer a payment plan.\n\n"
            "Reply and I'll tell you more.\n\nMaya | Velocity LA"
        ),
    },
    {
        "touch": 7,
        "channel": "SMS",
        "subject": "Last chance",
        "message": "Hey {name}, last message from me — I'll hold a spot through Friday. After that I'll release it. Want it? 🔑",
    },
]


def get_next_touch(lead_id: int) -> dict | None:
    db = get_db()
    try:
        sent = db.query(NurtureEvent).filter(NurtureEvent.lead_id == lead_id).count()
        return NURTURE_SEQUENCE[sent] if sent < len(NURTURE_SEQUENCE) else None
    finally:
        db.close()


def log_nurture_event(lead_id: int, touch: dict) -> None:
    db = get_db()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        first_name = lead.name.split()[0] if lead else "there"
        event = NurtureEvent(
            lead_id=lead_id,
            touch_number=touch["touch"],
            channel=touch["channel"],
            subject=touch.get("subject", ""),
            message=touch["message"].format(name=first_name),
        )
        db.add(event)
        db.commit()
    finally:
        db.close()
