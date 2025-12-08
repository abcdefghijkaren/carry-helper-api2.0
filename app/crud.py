# app/crud.py
from datetime import datetime
from typing import Optional, Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas


# =====================
# Users
# =====================

def create_user(db: Session, user_in: schemas.UserCreate) -> models.Users:
    db_user = models.Users(
        user_name=user_in.user_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Users]:
    return (
        db.query(models.Users)
        .order_by(models.Users.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user(db: Session, user_id: int) -> Optional[models.Users]:
    # 注意：這裡是 users.user_id
    return (
        db.query(models.Users)
        .filter(models.Users.user_id == user_id)
        .first()
    )


# =====================
# Events
# =====================

def create_event(db: Session, ev_in: schemas.EventCreate) -> models.Events:
    db_user = get_user(db, ev_in.user_id)
    if not db_user:
        raise ValueError(f"User with user_id={ev_in.user_id} not found")

    db_event = models.Events(
        user_id=db_user.user_id,
        user_name=db_user.user_name,
        act_type=ev_in.act_type,
        title=ev_in.title,
        location=ev_in.location,
        start_time=ev_in.start_time,
        end_time=ev_in.end_time,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def list_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.Events]:
    return (
        db.query(models.Events)
        .order_by(models.Events.start_time.is_(None), models.Events.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event(db: Session, event_id: int) -> Optional[models.Events]:
    return (
        db.query(models.Events)
        .filter(models.Events.id == event_id)
        .first()
    )


def list_events_for_user(db: Session, user_id: int) -> List[models.Events]:
    return (
        db.query(models.Events)
        .filter(models.Events.user_id == user_id)
        .order_by(models.Events.start_time.is_(None), models.Events.start_time.asc())
        .all()
    )


# =====================
# Event Items
# =====================

def create_event_item(
    db: Session, item_in: schemas.EventItemCreate
) -> models.EventItems:
    db_event = get_event(db, item_in.event_id)
    if not db_event:
        raise ValueError(f"Event with id={item_in.event_id} not found")

    db_item = models.EventItems(
        user_id=db_event.user_id,
        user_name=db_event.user_name,
        event_id=item_in.event_id,
        item_name=item_in.item_name,
        is_required=item_in.is_required,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def list_event_items(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.EventItems]:
    return (
        db.query(models.EventItems)
        .order_by(models.EventItems.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_item(db: Session, item_id: int) -> Optional[models.EventItems]:
    return (
        db.query(models.EventItems)
        .filter(models.EventItems.id == item_id)
        .first()
    )


def list_items_for_event(
    db: Session, event_id: int
) -> List[models.EventItems]:
    return (
        db.query(models.EventItems)
        .filter(models.EventItems.event_id == event_id)
        .order_by(models.EventItems.id.asc())
        .all()
    )


# =====================
# Reminder Logs
# =====================

def create_reminder_log(
    db: Session, r_in: schemas.ReminderLogCreate
) -> models.ReminderLogs:
    db_user = get_user(db, r_in.user_id)
    if not db_user:
        raise ValueError(f"User with user_id={r_in.user_id} not found")

    db_event = get_event(db, r_in.event_id)
    if not db_event:
        raise ValueError(f"Event with id={r_in.event_id} not found")

    db_log = models.ReminderLogs(
        user_id=db_user.user_id,
        user_name=db_user.user_name,
        event_id=r_in.event_id,
        reminder_text=r_in.reminder_text,
        triggered_by=r_in.triggered_by,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def list_reminder_logs(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.ReminderLogs]:
    return (
        db.query(models.ReminderLogs)
        .order_by(models.ReminderLogs.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reminder_log(db: Session, log_id: int) -> Optional[models.ReminderLogs]:
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.id == log_id)
        .first()
    )


def list_reminders_for_user(
    db: Session, user_id: int
) -> List[models.ReminderLogs]:
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.user_id == user_id)
        .order_by(models.ReminderLogs.created_at.desc())
        .all()
    )


# =====================
# Recommendation Logic
# =====================

def _get_main_shoe_for_act(db: Session, act_type: str) -> Optional[str]:
    """
    從規則表中找出此 act_type 最常用的鞋子類型（這裡簡化抓第一筆有鞋子的規則）
    """
    rule = (
        db.query(models.ActivityItemRule)
        .filter(
            models.ActivityItemRule.act_type == act_type,
            models.ActivityItemRule.shoe_type.isnot(None),
        )
        .first()
    )
    return rule.shoe_type if rule else None


def _get_items_for_event(
    db: Session, act_type: str, shoe_type: str
) -> Dict[str, int]:
    """
    根據活動類型 + 鞋子，從規則表抓出建議物品與權重
    """
    rules = (
        db.query(models.ActivityItemRule)
        .filter(models.ActivityItemRule.act_type == act_type)
        .filter(
            or_(
                models.ActivityItemRule.shoe_type.is_(None),
                models.ActivityItemRule.shoe_type == shoe_type,
            )
        )
        .all()
    )

    scores: Dict[str, int] = {}
    for r in rules:
        scores[r.item_name] = scores.get(r.item_name, 0) + (r.base_priority or 0)
    return scores


def infer_recommendations(
    db: Session,
    user_id: int,
    shoe_type: str,
    current_time: Optional[datetime] = None,
):
    """
    推算「推薦攜帶項目」的核心邏輯：

    1. 找出 user_id 未來的行程（按照 start_time 排序）
    2. current_event = 最接近 current_time 的下一個行程
       next_event    = 其下一個行程（如果有的話）
    3. 判斷鞋子：
       - 若使用者穿的是 next_event 的鞋子且 != current_event 的鞋子
         => 推薦項目 = current_event + next_event 需要的物品
       - 否則只推薦 current_event 的物品
    """

    if current_time is None:
        current_time = datetime.utcnow()

    upcoming: List[models.Events] = (
        db.query(models.Events)
        .filter(
            models.Events.user_id == user_id,
            models.Events.start_time >= current_time,
        )
        .order_by(models.Events.start_time.asc())
        .limit(2)
        .all()
    )

    if not upcoming:
        return None, None, []

    current_event = upcoming[0]
    next_event = upcoming[1] if len(upcoming) > 1 else None

    current_shoe = (
        _get_main_shoe_for_act(db, current_event.act_type)
        if current_event.act_type
        else None
    )

    include_next = False
    next_shoe = None
    if next_event and next_event.act_type:
        next_shoe = _get_main_shoe_for_act(db, next_event.act_type)
        # 只有在「穿的是下一個行程的鞋」且「不是現在行程預設鞋」時，才合併下一個行程的物品
        if next_shoe and shoe_type == next_shoe and shoe_type != current_shoe:
            include_next = True

    # 先加入目前行程的物品
    scores = {}
    if current_event.act_type:
        scores.update(_get_items_for_event(db, current_event.act_type, shoe_type))

    # 視需要合併下一個行程
    if include_next and next_event and next_event.act_type:
        next_scores = _get_items_for_event(db, next_event.act_type, shoe_type)
        for item_name, sc in next_scores.items():
            scores[item_name] = scores.get(item_name, 0) + sc

    # 依權重排序
    sorted_items = [
        name for name, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    ]

    # 若沒合併，就讓 next_event = None 比較清楚
    if not include_next:
        next_event = None

    return current_event, next_event, sorted_items
