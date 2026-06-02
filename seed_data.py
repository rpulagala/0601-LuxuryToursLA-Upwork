"""
Generates realistic demo leads across all pipeline stages.
Run directly:  python seed_data.py
Or called from the app on first load.
"""
import random
from datetime import datetime, timedelta
from database import init_db, get_db, Lead, Conversation, Booking, NurtureEvent

FIRST_NAMES = [
    "James","Marcus","Tyler","Kevin","Brian","Jason","Chris","Ryan","David","Michael",
    "Alex","Jordan","Daniel","Nathan","Eric","Brandon","Justin","Samuel","Derek","Aaron",
    "Ashley","Sofia","Priya","Emily","Sarah","Jessica","Amanda","Megan","Lauren","Rachel",
    "Stephanie","Kimberly","Vanessa","Lisa","Monica","Yuki","Isabella","Olivia","Emma","Ava",
    "Carlos","Roberto","Mohammed","Kai","Leo","Ethan","Owen","Liam","Noah","Lucas",
    "Zoe","Chloe","Madison","Natalie","Alexis","Hannah","Grace","Ella","Scarlett","Victoria",
    "Tony","Ben","Sean","Patrick","Greg","Jake","Matt","Cole","Blake","Trevor",
    "Mei","Aisha","Fatima","Layla","Nina","Diana","Elena","Rosa","Angela","Tanya",
    "Wesley","Marcus","Darius","Tyrone","Malik","Jamal","Keon","Deon","Jalen","Andre",
    "Sandra","Brianna","Jasmine","Keisha","Tamara","Latoya","Monique","Shonda","Imani","Alicia",
]

LAST_NAMES = [
    "Johnson","Smith","Chen","Rodriguez","Patel","Kim","Williams","Brown","Jones","Davis",
    "Miller","Wilson","Moore","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin",
    "Thompson","Garcia","Martinez","Robinson","Clark","Lewis","Lee","Walker","Hall","Allen",
    "Young","King","Wright","Scott","Torres","Nguyen","Hill","Flores","Green","Adams",
    "Nelson","Baker","Gonzalez","Carter","Mitchell","Perez","Roberts","Turner","Phillips","Campbell",
]

CARS = [
    "Lamborghini Huracán",
    "Ferrari 488 GTB",
    "McLaren 720S",
    "Porsche 911 GT3 RS",
    "Rolls-Royce Ghost",
]

PRICE_MAP = {
    "Lamborghini Huracán":  599.0,
    "Ferrari 488 GTB":      549.0,
    "McLaren 720S":         649.0,
    "Porsche 911 GT3 RS":   499.0,
    "Rolls-Royce Ghost":    449.0,
}

SOURCES = ["Website", "Instagram", "TikTok", "Google Ads", "Friend / Referral"]

CITIES = [
    "Beverly Hills, CA", "West Hollywood, CA", "Santa Monica, CA",
    "Bel Air, CA", "Malibu, CA", "Manhattan Beach, CA",
    "Calabasas, CA", "Sherman Oaks, CA", "Pasadena, CA",
    "Brentwood, CA", "Encino, CA", "Studio City, CA",
    "Los Angeles, CA", "Culver City, CA", "Marina del Rey, CA",
]

TEAM_MEMBERS = ["John Carter", "Mike Johnson", "Sarah Williams", "David Brown"]

DATES = [
    "This Saturday","This Sunday","Next Saturday","Next Sunday",
    "Weekend of Jul 12","Weekend of Jul 19","Weekend of Jul 26",
    "Saturday, Aug 2","Saturday, Aug 9","Saturday, Aug 16",
    "Mid-July","Late July","Early August","Mid-August",
    "Flexible — anytime in July","Flexible — anytime in August",
]

BUDGETS_HIGH = ["$1,000+", "$1,500+", "Over $1,000", "Budget is not an issue"]
BUDGETS_MID  = ["$500–$1,000", "Around $700", "Around $800", "$500 to $1,000"]
BUDGETS_LOW  = ["Under $500", "Around $400", "Around $300–$400", "Looking for something affordable"]

GROUPS_LARGE = ["3", "4", "5", "4 people", "Group of 5", "3 of us"]
GROUPS_SMALL = ["1", "2", "Solo", "Just me", "My partner and I", "2 of us"]

QUALIFIED_CONVOS = [
    [
        ("assistant", "Hey {name}! Welcome to Velocity LA — which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"),
        ("user",      "Definitely the {car}!"),
        ("assistant", "Excellent choice — the {car} is an incredible machine. Do you have a date in mind?"),
        ("user",      "{date} works for me"),
        ("assistant", "Perfect, that works! Will it be just you or are you bringing people along?"),
        ("user",      "{group} of us"),
        ("assistant", "Love it! And roughly what budget are you working with for the experience?"),
        ("user",      "{budget}"),
        ("assistant", "That's perfect — you're all set for an unforgettable experience. Ready to lock in your spot?"),
    ],
    [
        ("assistant", "Hi {name}! Thanks for your interest in Velocity LA. Which exotic car caught your eye — Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"),
        ("user",      "I've always wanted to drive a {car}"),
        ("assistant", "Great taste — the {car} never disappoints. When are you thinking of coming in?"),
        ("user",      "Probably {date}"),
        ("assistant", "That works perfectly! Is this a solo experience or are you bringing friends?"),
        ("user",      "{group} people total"),
        ("assistant", "Awesome! Last question — what's your approximate budget for the experience?"),
        ("user",      "I'm thinking {budget}"),
        ("assistant", "That fits our packages perfectly. I can get you a booking link right now — want me to send that over?"),
    ],
    [
        ("assistant", "Hey {name}! Welcome to Velocity LA — excited to help you plan your dream drive. Which car interests you most?"),
        ("user",      "The {car} looks amazing on your page"),
        ("assistant", "The {car} is one of our most popular! Do you have a preferred date or are you flexible?"),
        ("user",      "I was thinking {date}"),
        ("assistant", "Nice, we have availability then! How many people will be joining you?"),
        ("user",      "{group}"),
        ("assistant", "Perfect group size. What budget range works for you?"),
        ("user",      "{budget}"),
        ("assistant", "You're all set — I'll send you a booking link to lock in that date!"),
    ],
]

CONTACTED_CONVOS = [
    [
        ("assistant", "Hey {name}! Welcome to Velocity LA — which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"),
        ("user",      "The {car} looks sick"),
        ("assistant", "Right? The {car} is absolutely wild on the road. Do you have a date in mind, or still exploring?"),
        ("user",      "Still figuring out timing, maybe {date}"),
        ("assistant", "No rush at all — whenever you're ready I can check availability. Just reply here and I'll get you sorted!"),
    ],
    [
        ("assistant", "Hi {name}! Thanks for reaching out to Velocity LA. Which car are you most excited about?"),
        ("user",      "Thinking about the {car}"),
        ("assistant", "The {car} is an incredible choice. When are you looking to come in?"),
        ("user",      "Not sure yet, maybe sometime in {date}"),
        ("assistant", "Totally fine — slots fill up fast so whenever you decide, let me know and I'll hold one for you!"),
    ],
]

NURTURE_TOUCHES = [
    {"touch": 1, "channel": "SMS",   "subject": "Checking in",
     "message": "Hey {name}! Just checking in — did you get a chance to think about your experience? Our {car} slots this weekend are filling up fast."},
    {"touch": 2, "channel": "Email", "subject": "What our guests say",
     "message": "Hi {name},\n\nA recent guest said: \"The {car} on the open road around LA was unlike anything I've ever driven. Absolutely worth it.\"\n\nWhenever you're ready, just reply!\n\nMaya | Velocity LA"},
    {"touch": 3, "channel": "SMS",   "subject": "What's holding you back?",
     "message": "Hi {name}, quick question — is it the price, the timing, or something else? No pressure, just want to help."},
    {"touch": 4, "channel": "Email", "subject": "FAQ before your first drive",
     "message": "Hi {name},\n\nTop questions:\n✅ Do I need a racing license? No.\n✅ How long? 60-90 mins.\n✅ Can friends watch? Yes!\n\nReady?\n\nMaya | Velocity LA"},
]

TIME_SLOTS = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]


def _make_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _make_email(name):
    parts = name.lower().split()
    suffix = random.choice(["gmail.com", "outlook.com", "icloud.com", "yahoo.com"])
    sep = random.choice([".", "_", ""])
    num = str(random.randint(1, 99)) if random.random() > 0.5 else ""
    return f"{parts[0]}{sep}{parts[1]}{num}@{suffix}"


def _make_phone():
    area = random.choice(["310", "323", "213", "424", "818", "626", "562", "714", "949", "619"])
    return f"+1 ({area}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def _fill(template, name, car, date, group, budget):
    first = name.split()[0]
    g = group.split()[0] if group else "2"
    return (template
            .replace("{name}", first)
            .replace("{car}", car)
            .replace("{date}", date)
            .replace("{group}", g)
            .replace("{budget}", budget))


def seed():
    init_db()
    db = get_db()
    try:
        db.query(NurtureEvent).delete()
        db.query(Conversation).delete()
        db.query(Booking).delete()
        db.query(Lead).delete()
        db.commit()

        now = datetime.utcnow()
        used_names = set()

        def unique_name():
            for _ in range(100):
                n = _make_name()
                if n not in used_names:
                    used_names.add(n)
                    return n
            return _make_name()

        leads_created = 0

        # ── 1. BOOKED (25 leads spread over last 30 days for chart data) ─────
        for i in range(25):
            name   = unique_name()
            car    = random.choice(CARS)
            date   = random.choice(DATES[:8])
            group  = random.choice(GROUPS_LARGE + GROUPS_SMALL)
            budget = random.choice(BUDGETS_HIGH + BUDGETS_MID)
            score  = round(random.uniform(8.0, 10.0), 1)
            g_num  = int(group.split()[0]) if group.split()[0].isdigit() else 2
            g_num  = max(1, min(g_num, 5))
            # Spread confirmed_at over last 30 days, skewed more recent
            days_ago = int(random.triangular(0, 30, 5))
            confirmed = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            lead = Lead(
                name=name, email=_make_email(name), phone=_make_phone(),
                city=random.choice(CITIES),
                source=random.choice(SOURCES), preferred_car=car,
                preferred_date=date, group_size=str(g_num), budget=budget,
                score=score, pipeline_stage="Booked", tag="Hot",
                created_at=confirmed - timedelta(hours=random.randint(2, 48)),
            )
            db.add(lead); db.flush()

            tmpl = random.choice(QUALIFIED_CONVOS)
            for j, (role, msg) in enumerate(tmpl):
                db.add(Conversation(
                    lead_id=lead.id, role=role,
                    message=_fill(msg, name, car, date, group, budget),
                    timestamp=confirmed - timedelta(hours=random.randint(2, 48), minutes=j * 15),
                ))

            price_val = PRICE_MAP.get(car, 499.0)
            db.add(Booking(
                lead_id=lead.id, slot_date=date,
                slot_time=random.choice(TIME_SLOTS), car=car,
                amount=f"${int(price_val)}",
                price=price_val,
                team_member=random.choice(TEAM_MEMBERS),
                confirmed_at=confirmed,
            ))
            leads_created += 1

        # ── 2. QUALIFIED HOT (22 leads, score 8–10) ───────────────────────────
        for i in range(22):
            name   = unique_name()
            car    = random.choice(CARS)
            date   = random.choice(DATES)
            group  = random.choice(GROUPS_LARGE)
            budget = random.choice(BUDGETS_HIGH)
            score  = round(random.uniform(8.0, 10.0), 1)

            lead = Lead(
                name=name, email=_make_email(name), phone=_make_phone(),
                city=random.choice(CITIES),
                source=random.choice(SOURCES), preferred_car=car,
                preferred_date=date, group_size=group.split()[0],
                budget=budget, score=score,
                pipeline_stage="Qualified", tag="Hot",
                created_at=now - timedelta(hours=random.randint(1, 96)),
            )
            db.add(lead); db.flush()

            tmpl = random.choice(QUALIFIED_CONVOS)
            for j, (role, msg) in enumerate(tmpl):
                db.add(Conversation(
                    lead_id=lead.id, role=role,
                    message=_fill(msg, name, car, date, group, budget),
                    timestamp=now - timedelta(hours=random.randint(1, 48), minutes=j * 12),
                ))
            leads_created += 1

        # ── 3. QUALIFIED WARM (20 leads, score 6–7) ───────────────────────────
        for i in range(20):
            name   = unique_name()
            car    = random.choice(CARS)
            date   = random.choice(DATES)
            group  = random.choice(GROUPS_SMALL)
            budget = random.choice(BUDGETS_MID)
            score  = round(random.uniform(6.0, 7.9), 1)

            lead = Lead(
                name=name, email=_make_email(name), phone=_make_phone(),
                city=random.choice(CITIES),
                source=random.choice(SOURCES), preferred_car=car,
                preferred_date=date, group_size=group.split()[0],
                budget=budget, score=score,
                pipeline_stage="Qualified", tag="Warm",
                created_at=now - timedelta(hours=random.randint(2, 120)),
            )
            db.add(lead); db.flush()

            tmpl = random.choice(QUALIFIED_CONVOS)
            for j, (role, msg) in enumerate(tmpl):
                db.add(Conversation(
                    lead_id=lead.id, role=role,
                    message=_fill(msg, name, car, date, group, budget),
                    timestamp=now - timedelta(hours=random.randint(2, 72), minutes=j * 12),
                ))
            leads_created += 1

        # ── 4. CONTACTED (30 leads) ───────────────────────────────────────────
        for i in range(30):
            name  = unique_name()
            car   = random.choice(CARS)
            date  = random.choice(DATES[8:])
            group = random.choice(GROUPS_SMALL + GROUPS_LARGE)
            n_touches = random.randint(0, 4)

            lead = Lead(
                name=name, email=_make_email(name), phone=_make_phone(),
                city=random.choice(CITIES),
                source=random.choice(SOURCES), preferred_car=car,
                preferred_date="", group_size="", budget="", score=0.0,
                pipeline_stage="Contacted", tag="New",
                created_at=now - timedelta(hours=random.randint(6, 168)),
            )
            db.add(lead); db.flush()

            tmpl = random.choice(CONTACTED_CONVOS)
            for j, (role, msg) in enumerate(tmpl):
                db.add(Conversation(
                    lead_id=lead.id, role=role,
                    message=_fill(msg, name, car, date, group, ""),
                    timestamp=now - timedelta(hours=random.randint(6, 120), minutes=j * 20),
                ))

            first = name.split()[0]
            for t in NURTURE_TOUCHES[:n_touches]:
                db.add(NurtureEvent(
                    lead_id=lead.id,
                    touch_number=t["touch"], channel=t["channel"],
                    subject=t["subject"],
                    message=t["message"].replace("{name}", first).replace("{car}", car),
                    sent_at=now - timedelta(hours=random.randint(1, 96)),
                ))
            leads_created += 1

        # ── 5. NEW LEAD (20 leads) ─────────────────────────────────────────────
        for i in range(20):
            name = unique_name()
            car  = random.choice(CARS)

            lead = Lead(
                name=name, email=_make_email(name), phone=_make_phone(),
                city=random.choice(CITIES),
                source=random.choice(SOURCES), preferred_car=car,
                preferred_date="", group_size="", budget="", score=0.0,
                pipeline_stage="New Lead", tag="New",
                created_at=now - timedelta(minutes=random.randint(1, 240)),
            )
            db.add(lead); db.flush()

            db.add(Conversation(
                lead_id=lead.id, role="assistant",
                message=(f"Hey {name.split()[0]}! Welcome to Velocity LA — "
                         f"which car are you dreaming of driving: Lamborghini, Ferrari, McLaren, Porsche, or Rolls-Royce?"),
                timestamp=now - timedelta(minutes=random.randint(1, 240)),
            ))
            leads_created += 1

        db.commit()
        print(f"Seeded {leads_created} leads successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    random.seed(42)
    seed()
    db = get_db()
    try:
        from collections import Counter
        leads = db.query(Lead).all()
        stages = Counter(l.pipeline_stage for l in leads)
        print("Pipeline breakdown:")
        for stage, count in sorted(stages.items()):
            print(f"  {stage:15} {count}")
        print(f"Bookings:       {db.query(Booking).count()}")
        print(f"Nurture events: {db.query(NurtureEvent).count()}")
        print(f"Conversations:  {db.query(Conversation).count()}")
    finally:
        db.close()
