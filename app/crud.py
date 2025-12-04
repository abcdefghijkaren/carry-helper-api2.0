# app/crud.py
from sqlalchemy.orm import Session

from app import models, schemas


# =====================
# Users
# =====================

def create_user(db: Session, user_in: schemas.UserCreate) -> models.Users:
    """
    建立新使用者：
    - user_id 由資料庫的 sequence 自動產生
    """
    db_user = models.Users(
        user_name=user_in.user_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.Users]:
    """
    取得使用者列表，依建立時間排序
    """
    return (
        db.query(models.Users)
        .order_by(models.Users.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user(db: Session, user_id: int) -> models.Users | None:
    """
    以 user_id（對外識別）取得使用者。
    注意：這裡是 users.user_id 不是 users.id。
    """
    return (
        db.query(models.Users)
        .filter(models.Users.user_id == user_id)
        .first()
    )


# =====================
# Events
# =====================

def create_event(db: Session, ev_in: schemas.EventCreate) -> models.Events:
    """
    建立事件：
    - 依 user_id 查出對應的 Users 記錄，填入 user_name
    - main.py 會先用 get_user 檢查使用者存在
    """
    db_user = get_user(db, ev_in.user_id)
    if not db_user:
        # 理論上 main 那邊已經檢查過，但這裡再防一層
        raise ValueError(f"User with user_id={ev_in.user_id} not found")

    db_event = models.Events(
        user_id=db_user.user_id,
        user_name=db_user.user_name,
        title=ev_in.title,
        location=ev_in.location,
        start_time=ev_in.start_time,
        end_time=ev_in.end_time,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def list_events(db: Session, skip: int = 0, limit: int = 100) -> list[models.Events]:
    """
    取得全部事件列表，依 start_time 排序（無 start_time 的排在後面）
    """
    return (
        db.query(models.Events)
        .order_by(models.Events.start_time.is_(None), models.Events.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event(db: Session, event_id: int) -> models.Events | None:
    """
    以 id 取得單一事件。
    """
    return (
        db.query(models.Events)
        .filter(models.Events.id == event_id)
        .first()
    )


def list_events_for_user(db: Session, user_id: int) -> list[models.Events]:
    """
    取得某使用者的所有事件：
    - 以 Events.user_id == users.user_id 查
    """
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
    """
    建立事件物品：
    - 透過 event_id 查出 Events，使用它的 user_id & user_name
    - 這樣就不用前端傳 user_name，避免不一致
    """
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
) -> list[models.EventItems]:
    """
    取得所有事件物品
    """
    return (
        db.query(models.EventItems)
        .order_by(models.EventItems.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event_item(db: Session, item_id: int) -> models.EventItems | None:
    """
    取得單一事件物品
    """
    return (
        db.query(models.EventItems)
        .filter(models.EventItems.id == item_id)
        .first()
    )


def list_items_for_event(
    db: Session, event_id: int
) -> list[models.EventItems]:
    """
    取得特定事件底下的所有物品
    """
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
    """
    建立提醒紀錄：
    - 依 user_id 查出 user_name
    - 可同時檢查 event 是否存在，避免寫入無效 event_id
    """
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
) -> list[models.ReminderLogs]:
    """
    取得全部提醒紀錄
    """
    return (
        db.query(models.ReminderLogs)
        .order_by(models.ReminderLogs.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_reminder_log(db: Session, log_id: int) -> models.ReminderLogs | None:
    """
    取得單一提醒紀錄
    """
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.id == log_id)
        .first()
    )


def list_reminders_for_user(
    db: Session, user_id: int
) -> list[models.ReminderLogs]:
    """
    取得某使用者的所有提醒紀錄：
    - 以 ReminderLogs.user_id（= users.user_id）查
    """
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.user_id == user_id)
        .order_by(models.ReminderLogs.created_at.desc())
        .all()
    )
