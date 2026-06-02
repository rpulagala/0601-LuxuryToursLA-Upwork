from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, default="")
    phone = Column(String, default="")
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


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    return SessionLocal()
