# app/models.py
from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey, Sequence
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    # 對應資料庫：
    # id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass)
    id = Column(Integer, primary_key=True, index=True)

    # 對外使用的使用者編號（有自己的 sequence：users_user_id_seq）
    # 對應：user_id integer NOT NULL DEFAULT nextval('users_user_id_seq'::regclass)
    user_id = Column(
        Integer,
        Sequence("users_user_id_seq"),  # 名稱對齊資料庫中的 sequence
        unique=True,
        nullable=False,
    )

    # 對應：user_name text NOT NULL
    user_name = Column(Text, nullable=False)

    # 對應：created_at timestamptz DEFAULT now()
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # 關聯：一個 user 對多個 events / event_items / reminder_logs
    events = relationship("Events", back_populates="user")
    event_items = relationship("EventItems", back_populates="user")
    reminder_logs = relationship("ReminderLogs", back_populates="user")


class Events(Base):
    __tablename__ = "events"

    # 對應：id integer NOT NULL DEFAULT nextval('events_id_seq'::regclass)
    id = Column(Integer, primary_key=True, index=True)

    # 對應：user_id integer NOT NULL
    # FK 對應到 users.user_id（不是 users.id）
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # 對應：user_name text NOT NULL
    # 建議由後端依 user_id 從 Users 表帶入，不讓前端任意改
    user_name = Column(Text, nullable=False)

    # 對應：title text NOT NULL
    title = Column(Text, nullable=False)

    # 對應：location text
    location = Column(Text)

    # 對應：start_time timestamptz
    start_time = Column(TIMESTAMP(timezone=True))

    # 對應：end_time timestamptz
    end_time = Column(TIMESTAMP(timezone=True))

    # 對應：created_at timestamptz DEFAULT now()
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # 關聯
    user = relationship("Users", back_populates="events")
    items = relationship("EventItems", back_populates="event")
    logs = relationship("ReminderLogs", back_populates="event")


class EventItems(Base):
    __tablename__ = "event_items"

    # 對應：id integer NOT NULL DEFAULT nextval('event_items_id_seq'::regclass)
    id = Column(Integer, primary_key=True, index=True)

    # 對應：user_id integer NOT NULL
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # 對應：user_name text NOT NULL
    user_name = Column(Text, nullable=False)

    # 對應：event_id integer NOT NULL
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    # 對應：item_name text NOT NULL
    item_name = Column(Text, nullable=False)

    # 對應：is_required boolean DEFAULT true
    is_required = Column(Boolean, default=True)

    # 對應：created_at timestamptz DEFAULT now()
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # 關聯
    event = relationship("Events", back_populates="items")
    user = relationship("Users", back_populates="event_items")


class ReminderLogs(Base):
    __tablename__ = "reminder_logs"

    # 對應：id integer NOT NULL DEFAULT nextval('reminder_logs_id_seq'::regclass)
    id = Column(Integer, primary_key=True, index=True)

    # 對應：user_id integer NOT NULL
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # 對應：user_name text NOT NULL
    user_name = Column(Text, nullable=False)

    # 對應：event_id integer NOT NULL
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    # 對應：reminder_text text NOT NULL
    reminder_text = Column(Text, nullable=False)

    # 對應：triggered_by text
    triggered_by = Column(Text)

    # 對應：created_at timestamptz DEFAULT now()
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # 關聯
    event = relationship("Events", back_populates="logs")
    user = relationship("Users", back_populates="reminder_logs")