# app/models.py
from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    events = relationship("Events", back_populates="user")


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(Text, nullable=False)
    location = Column(Text)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="events")
    items = relationship("EventItems", back_populates="event")
    logs = relationship("ReminderLogs", back_populates="event")


class EventItems(Base):
    __tablename__ = "event_items"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    item_name = Column(Text, nullable=False)
    is_required = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    event = relationship("Events", back_populates="items")


class ReminderLogs(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"))
    reminder_text = Column(Text, nullable=False)
    triggered_by = Column(Text)   # sensor / user / app
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    event = relationship("Events", back_populates="logs")
