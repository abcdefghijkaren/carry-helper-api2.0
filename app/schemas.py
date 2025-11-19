# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Users
class UserCreate(BaseModel):
    name: str

class UserRead(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# Events
class EventCreate(BaseModel):
    user_id: int
    title: str
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class EventRead(BaseModel):
    id: int
    user_id: int
    title: str
    location: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# Event items
class EventItemCreate(BaseModel):
    event_id: int
    item_name: str
    is_required: Optional[bool] = True

class EventItemRead(BaseModel):
    id: int
    event_id: int
    item_name: str
    is_required: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# Reminder logs
class ReminderLogCreate(BaseModel):
    user_id: int
    event_id: int
    reminder_text: str
    triggered_by: Optional[str] = None

class ReminderLogRead(BaseModel):
    id: int
    user_id: int
    event_id: int
    reminder_text: str
    triggered_by: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
