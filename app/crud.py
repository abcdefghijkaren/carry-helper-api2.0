from datetime import datetime
from typing import Optional, Dict, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas


# =====================
# Users
# =====================

def create_user(db: Session, user_in: schemas.UserCreate) -> models.Users:
    """
    建立使用者。
    對應資料表欄位：
    - users.id          (serial PK)
    - users.user_id     (serial or sequence，對外用的 ID)
    - users.user_name   (NOT NULL)
    - users.created_at  (default now())
    """
    # schemas.UserCreate 可能叫 name 或 user_name，這裡做一下兼容
    user_name = getattr(user_in, "user_name", None) or getattr(user_in, "name", None)
    if not user_name:
        raise ValueError("UserCreate 需要 name 或 user_name 欄位")

    db_user = models.Users(user_name=user_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Users]:
    return (
        db.query(models.Users)
        .order_by(models.Users.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user(db: Session, user_id: int) -> Optional[models.Users]:
    """
    注意：這裡的 user_id 是對外使用的 users.user_id（不是 PK id）。
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
    從 APP 端接收一筆行程，寫入 events 表，之後推薦演算法會用。

    要求 schemas.EventCreate 欄位：
    - user_id:   int
    - user_name: str
    - act_type:  str   (class / meet / bill / snack / exercise ...)
    - title:     str
    - location:  Optional[str]
    - start_time: datetime
    - end_time:   datetime
    """

    db_ev = models.Events(
        user_id=ev_in.user_id,
        user_name=ev_in.user_name,
        act_type=ev_in.act_type,
        title=ev_in.title,
        location=ev_in.location,
        start_time=ev_in.start_time,
        end_time=ev_in.end_time,
    )

    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)
    return db_ev


def list_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.Events]:
    """
    列出全部行程（依開始時間排序）。
    """
    return (
        db.query(models.Events)
        .order_by(models.Events.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_event(db: Session, event_id: int) -> Optional[models.Events]:
    """
    依 events.id 取得單一行程。
    """
    return (
        db.query(models.Events)
        .filter(models.Events.id == event_id)
        .first()
    )


def list_events_for_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Events]:
    """
    列出某位使用者的所有行程（依開始時間排序）。
    user_id 為 users.user_id（對外 ID）。
    """
    return (
        db.query(models.Events)
        .filter(models.Events.user_id == user_id)
        .order_by(models.Events.start_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# =====================
# Event Items（如果之後要用，可再調整）
# =====================

def create_event_item(db: Session, item_in: schemas.EventItemCreate) -> models.EventItems:
    """
    若有額外為某 event 手動新增 item，可用這個。
    目前推薦主要走 activity_item_rules，所以這段可視需求簡化或保留。
    """
    db_item = models.EventItems(
        user_id=item_in.user_id,
        user_name=item_in.user_name,
        event_id=item_in.event_id,
        item_name=item_in.item_name,
        is_required=item_in.is_required,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def list_event_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.EventItems]:
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
    db: Session, event_id: int, skip: int = 0, limit: int = 100
) -> List[models.EventItems]:
    return (
        db.query(models.EventItems)
        .filter(models.EventItems.event_id == event_id)
        .order_by(models.EventItems.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# =====================
# Reminder Logs（備用，看你後面要不要記錄提醒紀錄）
# =====================

def create_reminder_log(
    db: Session, r_in: schemas.ReminderLogCreate
) -> models.ReminderLogs:
    db_log = models.ReminderLogs(
        user_id=r_in.user_id,
        user_name=r_in.user_name,
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


def get_reminder_log(
    db: Session, log_id: int
) -> Optional[models.ReminderLogs]:
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.id == log_id)
        .first()
    )


def list_reminders_for_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.ReminderLogs]:
    return (
        db.query(models.ReminderLogs)
        .filter(models.ReminderLogs.user_id == user_id)
        .order_by(models.ReminderLogs.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# =====================
# Recommendation Helpers & Core Logic
# =====================

def _get_main_shoe_for_act(db: Session, act_type: str) -> Optional[str]:
    """
    取得某個活動類型的「預設鞋型」。

    通常在 activity_item_rules 表中，會針對同一個 act_type
    重複出現相同的 shoe_type（例如：class → sneaker, meet → formal），
    這裡只取第一筆有設定 shoe_type 的規則作為預設值。
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
    針對「單一活動 act_type + 使用者目前穿的鞋型 shoe_type」，計算每個物品的分數。

    規則：
    - act_type 必須相同
    - rule.shoe_type == shoe_type → 視為符合條件
    - rule.shoe_type IS NULL      → 通用規則，任何鞋型都適用

    回傳：
    - item_name → score 的 dict，例如：
      { "id_card": 10, "laptop": 9, ... }
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
        if not r.item_name:
            continue
        base = r.base_priority or 0
        scores[r.item_name] = scores.get(r.item_name, 0) + base

    return scores


def infer_recommendations(
    db: Session,
    user_id: int,
    shoe_type: str,
    current_time: Optional[datetime] = None,
) -> Tuple[Optional[models.Events], Optional[models.Events], List[str]]:
    """
    核心推薦邏輯。

    步驟：
    1. 依 user_id 與 current_time 找出最近的 1～2 筆未來行程
       → current_event 與 next_event。
    2. 由 activity_item_rules 推估 current_event 與 next_event 的預設鞋型。
    3. 判斷是否應該合併 next_event：
         若 user_wearing_shoe == next_event_shoe
         且 user_wearing_shoe != current_event_shoe
         → 視為會從 current_event 直接接續 next_event，一起考慮。
    4. 針對要考慮的活動：
         - 根據 act_type + shoe_type 取出所有符合規則的物品
         - 以 base_priority 累加分數
    5. 依分數由高到低排序物品名稱，產生推薦清單。

    回傳：
    (current_event, next_event_or_None, sorted_item_list)
    """
    # 若未指定 current_time，預設使用目前 UTC 時間
    if current_time is None:
        current_time = datetime.utcnow()

    # Step 1: 找出最近兩個未來行程
    upcoming = (
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

    # Step 2: 推估這兩個行程的預設鞋型
    current_shoe = (
        _get_main_shoe_for_act(db, current_event.act_type)
        if current_event.act_type
        else None
    )

    include_next = False
    next_shoe: Optional[str] = None

    if next_event and next_event.act_type:
        next_shoe = _get_main_shoe_for_act(db, next_event.act_type)

        # 核心判斷：
        # 若使用者實際穿的鞋 == next_event 的預設鞋型
        # 且 != current_event 的預設鞋型
        # → 視為會直接接續 next_event，一次出門要滿足兩個行程
        if next_shoe and shoe_type == next_shoe and shoe_type != current_shoe:
            include_next = True

    # Step 3: 先取 current_event 的物品分數
    scores: Dict[str, int] = {}
    if current_event.act_type:
        cur_scores = _get_items_for_event(db, current_event.act_type, shoe_type)
        for name, sc in cur_scores.items():
            scores[name] = scores.get(name, 0) + sc

    # Step 4: 若判定需要，合併 next_event 的物品分數
    if include_next and next_event and next_event.act_type:
        next_scores = _get_items_for_event(db, next_event.act_type, shoe_type)
        for name, sc in next_scores.items():
            scores[name] = scores.get(name, 0) + sc
    else:
        # 不合併時，next_event 對外就視為 None
        next_event = None

    # Step 5: 依分數由高到低排序，輸出物品名稱清單
    sorted_items = [
        name for name, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    ]

    return current_event, next_event, sorted_items
