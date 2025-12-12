from datetime import datetime
from typing import Optional, Dict, List, Tuple, Set

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
# Find CommonItemsByShoe
# =====================

def get_common_items_by_shoe_id(db: Session, shoe_id: int) -> dict:
    rows = (
        db.query(models.CommonItemsByShoe)
        .filter(models.CommonItemsByShoe.shoe_id == shoe_id)
        .all()
    )

    if not rows:
        return {"shoe_id": shoe_id, "shoe_type": None, "items": []}

    shoe_type = rows[0].shoe_type
    items = [r.item_name for r in rows]

    return {
        "shoe_id": shoe_id,
        "shoe_type": shoe_type,
        "items": items
    }



# =====================
# Recommendation Helpers & Core Logic
# =====================


def _get_main_shoe_for_act(db: Session, act_type: str) -> Optional[str]:
    rule = (
        db.query(models.ActivityItemRule)
        .filter(
            models.ActivityItemRule.act_type == act_type,
            models.ActivityItemRule.shoe_type.isnot(None),
        )
        .first()
    )
    return rule.shoe_type if rule else None


TOP3_MIN_SCORE = 7
EXTRA_MIN_SCORE = 7
TOP3_LIMIT = 3
EXTRA_MAX = 5  # 可能到第4、第5（最多 5 個）


def _rules_for_act(db: Session, act_type: str, shoe_type: str) -> List[models.ActivityItemRule]:
    """
    取出某 act_type 在目前鞋型下可用的規則（含通用 shoe_type=NULL 規則）。
    """
    return (
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


def get_activity_extra_recs(
    db: Session,
    current_act_type: str,
    shoe_type: str,
    next_act_type: Optional[str] = None,
    include_next: bool = False,
) -> List[str]:
    """
    只從 activity_item_rules 產生「額外推薦」項目（不含必帶/共同/鞋子額外）。

    規則：
    1) 先挑 Top3：分數 >= 7 的前三名
    2) 第4、第5...：只收 (重疊) 或 (分數>=7) 的候選，最多到 5 個
    """

    # 1) 收集 current / next 的規則（只用非 default 的做「額外推薦」）
    cur_rules = _rules_for_act(db, current_act_type, shoe_type) if current_act_type else []
    nxt_rules = []
    if include_next and next_act_type:
        nxt_rules = _rules_for_act(db, next_act_type, shoe_type)

    # 2) 建 overlap（同 item 同時出現在 current+next）
    cur_set: Set[str] = set([r.item_name for r in cur_rules if r.item_name])
    nxt_set: Set[str] = set([r.item_name for r in nxt_rules if r.item_name])
    overlap: Set[str] = cur_set.intersection(nxt_set) if include_next else set()

    # 3) 累積分數（只算非 default）
    scores: Dict[str, int] = {}

    def acc(rules: List[models.ActivityItemRule]):
        for r in rules:
            if not r.item_name:
                continue
            if getattr(r, "is_default", False):
                continue  # 額外推薦不包含 default
            scores[r.item_name] = scores.get(r.item_name, 0) + (r.base_priority or 0)

    acc(cur_rules)
    acc(nxt_rules)

    # 4) 排序候選
    candidates = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    # 5) Top3（>=7）
    top3 = [name for name, sc in candidates if sc >= TOP3_MIN_SCORE][:TOP3_LIMIT]

    # 6) 第4、第5...：只收 (重疊) 或 (>=7)
    extra: List[str] = []
    for name, sc in candidates:
        if name in top3:
            continue
        if len(top3) + len(extra) >= EXTRA_MAX:
            break
        if (name in overlap) or (sc >= EXTRA_MIN_SCORE):
            extra.append(name)

    return top3 + extra

def infer_recommendations(
    db: Session,
    user_id: int,
    shoe_type: str,
    current_time: Optional[datetime] = None,
) -> Tuple[Optional[models.Events], Optional[models.Events], List[str]]:
    """
    給 /recommendations 或 /detect_shoe 使用：
    - 找出 current_event / next_event
    - 判斷 include_next（鞋子是否代表會接續下一行程）
    - 只回傳「activity_item_rules 的額外推薦」items（Top3>=7 + 第4第5條件）
    """

    if current_time is None:
        current_time = datetime.utcnow()

    # 1) 找最近兩筆未來行程
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

    # 2) 判斷 include_next
    current_shoe = _get_main_shoe_for_act(db, current_event.act_type) if current_event.act_type else None
    include_next = False

    if next_event and next_event.act_type:
        next_shoe = _get_main_shoe_for_act(db, next_event.act_type)
        if next_shoe and shoe_type == next_shoe and shoe_type != current_shoe:
            include_next = True

    # 3) 只取 activity_item_rules 額外推薦（你要的那一包）
    items = get_activity_extra_recs(
        db=db,
        current_act_type=current_event.act_type,
        shoe_type=shoe_type,
        next_act_type=(next_event.act_type if next_event else None),
        include_next=include_next,
    )

    # 若沒有 include_next，就不要對外回 next_event（避免前端誤解）
    if not include_next:
        next_event = None

    return current_event, next_event, items
