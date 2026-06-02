from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, inspect, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leads.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine)
Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, default="")
    phone = Column(String, default="")
    city = Column(String, default="")
    source = Column(String, default="Website Form")
    preferred_car = Column(String, default="")
    preferred_date = Column(String, default="")
    group_size = Column(String, default="")
    budget = Column(String, default="")
    score = Column(Float, default=0.0)
    pipeline_stage = Column(String, default="New Lead")
    tag = Column(String, default="New")
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="lead", cascade="all, delete-orphan")
    nurture_events = relationship("NurtureEvent", back_populates="lead", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="lead", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    role = Column(String)  # "user" or "assistant"
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="conversations")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    slot_date = Column(String)
    slot_time = Column(String)
    car = Column(String)
    amount = Column(String, default="$500")
    price = Column(Float, default=499.0)
    team_member = Column(String, default="")
    confirmed_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="bookings")


class NurtureEvent(Base):
    __tablename__ = "nurture_events"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    touch_number = Column(Integer)
    channel = Column(String)
    subject = Column(String, default="")
    message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="nurture_events")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    doc_type = Column(String)   # "drivers_license", "passenger_id", "selfie"
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="documents")


def init_db():
    Base.metadata.create_all(engine)
    # Safe column additions for upgrades on existing DBs
    inspector = inspect(engine)
    with engine.connect() as conn:
        existing_tables = inspector.get_table_names()
        if "leads" in existing_tables:
            lead_cols = [c["name"] for c in inspector.get_columns("leads")]
            if "city" not in lead_cols:
                conn.execute(text("ALTER TABLE leads ADD COLUMN city VARCHAR DEFAULT ''"))
        if "bookings" in existing_tables:
            booking_cols = [c["name"] for c in inspector.get_columns("bookings")]
            if "price" not in booking_cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN price FLOAT DEFAULT 499.0"))
            if "team_member" not in booking_cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN team_member VARCHAR DEFAULT ''"))
        conn.commit()


def get_db():
    return SessionLocal()
