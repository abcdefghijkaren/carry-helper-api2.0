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

COMMON_FIXED = ["phone", "wallet", "key"]

EXTRA_TOP_N = 3          # 先出 3 個
EXTRA_MAX = 5            # 最多到第 4、5 個
EXTRA_SCORE_GATE = 7     # 分數 >= 7 才能進入第 4、5 個（除非重疊）


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


def _get_rules_for_event(
    db: Session, act_type: str, shoe_type: str
) -> List[models.ActivityItemRule]:
    """
    抓出符合 act_type + shoe_type 的規則（包含 is_default / base_priority）
    - shoe_type 相同 or rule.shoe_type is NULL (通用)
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


def infer_recommendations(
    db: Session,
    user_id: int,
    shoe_type: str,
    current_time: Optional[datetime] = None,
) -> Tuple[Optional[models.Events], Optional[models.Events], List[str]]:
    """
    回傳（current_event, next_event_or_None, items）
    items = MUST + EXTRA（已去重、控制數量、不吵版本）
    """
    if current_time is None:
        current_time = datetime.utcnow()

    # 1) 最近兩筆未來行程
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

    # 2) 判斷是否接續下一行程 include_next
    current_shoe = _get_main_shoe_for_act(db, current_event.act_type) if current_event.act_type else None
    include_next = False
    next_shoe = None
    if next_event and next_event.act_type:
        next_shoe = _get_main_shoe_for_act(db, next_event.act_type)
        if next_shoe and shoe_type == next_shoe and shoe_type != current_shoe:
            include_next = True

    # 3) 取規則（current / next）
    cur_rules = _get_rules_for_event(db, current_event.act_type, shoe_type) if current_event.act_type else []
    nxt_rules = _get_rules_for_event(db, next_event.act_type, shoe_type) if (include_next and next_event and next_event.act_type) else []

    # 4) Must：固定三項 + 鞋子額外（如果你是從 common_items_by_shoe 合併，這裡請改成你現有的函式）
    # 這裡假設你已經有 crud.get_common_items_by_shoe_id 或依 shoe_type 查的函式
    # 先用 shoe_type 版本示意（你可換成 shoe_id 版本）
    shoe_extra = []
    try:
        shoe_extra = [
            r.item_name
            for r in db.query(models.CommonItemsByShoe)
            .filter(models.CommonItemsByShoe.shoe_type == shoe_type)
            .all()
        ]
    except Exception:
        shoe_extra = []

    must: List[str] = []
    for x in COMMON_FIXED + shoe_extra:
        if x not in must:
            must.append(x)

    # 加入 default（current + 若 include_next 則 next）
    def _add_defaults(rules: List[models.ActivityItemRule]):
        for r in rules:
            if getattr(r, "is_default", False):
                if r.item_name and r.item_name not in must:
                    must.append(r.item_name)

    _add_defaults(cur_rules)
    _add_defaults(nxt_rules)

    # 5) Extra：先計分（只看非 default）
    # 同時建立「重疊集合」：出現在 current 和 next 的 item
    cur_items_set: Set[str] = set([r.item_name for r in cur_rules if r.item_name])
    nxt_items_set: Set[str] = set([r.item_name for r in nxt_rules if r.item_name])
    overlap_items: Set[str] = cur_items_set.intersection(nxt_items_set) if include_next else set()

    scores: Dict[str, int] = {}

    def _accumulate_non_default(rules: List[models.ActivityItemRule]):
        for r in rules:
            if not r.item_name:
                continue
            if getattr(r, "is_default", False):
                continue
            base = r.base_priority or 0
            scores[r.item_name] = scores.get(r.item_name, 0) + base

    _accumulate_non_default(cur_rules)
    _accumulate_non_default(nxt_rules)

    # 把已在 must 的排除掉（避免重複吵）
    for m in must:
        scores.pop(m, None)

    # 排序候選（高分在前）
    candidates = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    extra: List[str] = []

    # 5-1) 先塞前 3 個（如果有）
    for name, _sc in candidates[:EXTRA_TOP_N]:
        extra.append(name)

    # 5-2) 再考慮第 4～5 個：必須 (重疊) 或 (>=7)
    for name, sc in candidates[EXTRA_TOP_N:]:
        if len(extra) >= EXTRA_MAX:
            break
        if (name in overlap_items) or (sc >= EXTRA_SCORE_GATE):
            extra.append(name)

    # 6) 最終 items（must + extra）
    items: List[str] = []
    for x in must + extra:
        if x not in items:
            items.append(x)

    # 若不 include_next，就不要對外回 next_event
    if not include_next:
        next_event = None

    return current_event, next_event, items
