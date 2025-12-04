# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# =====================
# Users
# =====================

class UserCreate(BaseModel):
    """
    建立使用者時只需要 user_name，
    user_id 由資料庫的 sequence 自動產生。
    """
    user_name: str


class UserRead(BaseModel):
    """
    對外回傳使用者資訊：
    - id: 資料庫內部主鍵
    - user_id: 對外識別用的使用者編號
    - user_name: 使用者名稱
    """
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
    """
    建立事件：
    - 必須帶 user_id，後端可根據 user_id 從 users 表查出 user_name
      再寫入 events.user_name（避免前端亂傳名字）。
    """
    user_id: int
    title: str
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime


class EventRead(BaseModel):
    """
    讀取事件時，一併回傳 user_id 與 user_name。
    """
    id: int
    user_id: int
    user_name: str
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
    """
    建立事件物品：
    - 前端只需提供 event_id, item_name, is_required
    - user_id / user_name 可以在後端依照 event.event_id 自動補上
    """
    event_id: int
    item_name: str
    is_required: Optional[bool] = True


class EventItemRead(BaseModel):
    """
    讀取事件物品：
    - 回傳 event_id + 該物品所屬 user 的 user_id / user_name
    """
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
    """
    建立提醒紀錄：
    - 由後端寫入時，可以只用 user_id, event_id，
      user_name 後端依 user_id 查出再寫入 reminder_logs.user_name
    """
    user_id: int
    event_id: int
    reminder_text: str
    triggered_by: Optional[str] = None


class ReminderLogRead(BaseModel):
    """
    讀取提醒紀錄：
    - 回傳 user_id, user_name, event_id 等完整資訊
    """
    id: int
    user_id: int
    user_name: str
    event_id: int
    reminder_text: str
    triggered_by: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True