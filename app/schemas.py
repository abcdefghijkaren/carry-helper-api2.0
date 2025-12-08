# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# =====================
# Users
# =====================

class UserCreate(BaseModel):
    user_name: str


class UserRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    created_at: datetime

    class Config:
        orm_mode = True


# =====================
# Events
# =====================

class EventCreate(BaseModel):
    user_id: int
    act_type: str  # class / exercise / bill / snack / meet...
    title: str
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime


class EventRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    act_type: Optional[str] = None
    title: str
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    created_at: datetime

    class Config:
        orm_mode = True


# =====================
# Event Items
# =====================

class EventItemCreate(BaseModel):
    event_id: int
    item_name: str
    is_required: Optional[bool] = True


class EventItemRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    event_id: int
    item_name: str
    is_required: Optional[bool] = True
    created_at: datetime

    class Config:
        orm_mode = True


# =====================
# Reminder Logs
# =====================

class ReminderLogCreate(BaseModel):
    user_id: int
    event_id: int
    reminder_text: str
    triggered_by: Optional[str] = None


class ReminderLogRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    event_id: int
    reminder_text: str
    triggered_by: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


# =====================
# Recommendation (推薦攜帶項目)
# =====================

class RecommendRequest(BaseModel):
    user_id: int
    shoe_type: str                    # 'sneaker' / 'formal' / 'slipper'
    current_time: Optional[datetime] = None  # 若為 None 則後端用現在時間


class RecommendResponse(BaseModel):
    current_event: Optional[EventRead]
    next_event: Optional[EventRead]
    items: List[str]                  # 推薦攜帶物品（英文短字）

    class Config:
        orm_mode = True
