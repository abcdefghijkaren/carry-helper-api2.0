# app/models.py
from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, Sequence
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # 對外識別的 user_id，使用資料庫中的 users_user_id_seq
    user_id = Column(
        Integer,
        Sequence("users_user_id_seq"),
        unique=True,
        nullable=False,
    )
    user_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    events = relationship("Events", back_populates="user")
    event_items = relationship("EventItems", back_populates="user")
    reminder_logs = relationship("ReminderLogs", back_populates="user")


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(Text, nullable=False)

    # 新增：活動類型（class / exercise / bill / snack / meet...）
    act_type = Column(Text)  # DB 允許 NULL，但應該由程式填入

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
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(Text, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    item_name = Column(Text, nullable=False)
    is_required = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    event = relationship("Events", back_populates="items")
    user = relationship("Users", back_populates="event_items")


class ReminderLogs(Base):
    __tablename__ = "reminder_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    user_name = Column(Text, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    reminder_text = Column(Text, nullable=False)
    triggered_by = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    event = relationship("Events", back_populates="logs")
    user = relationship("Users", back_populates="reminder_logs")


class ActivityItemRule(Base):
    """
    活動-物品規則：用來實作「智慧推薦攜帶項目」
    """
    __tablename__ = "activity_item_rules"

    id = Column(Integer, primary_key=True, index=True)
    act_type = Column(Text, nullable=False)       # class / exercise / bill / snack / meet
    item_name = Column(Text, nullable=False)      # laptop / bottle / wallet ...
    base_priority = Column(Integer, nullable=False, default=1)
    shoe_type = Column(Text)                      # sneaker / formal / slipper / NULL
    time_tag = Column(Text)                       # 可先不使用
    is_default = Column(Boolean, nullable=False, default=False)
