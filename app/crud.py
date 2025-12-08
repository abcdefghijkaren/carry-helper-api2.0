from datetime import datetime
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models


def _get_main_shoe_for_act(db: Session, act_type: str) -> Optional[str]:
    """
    Get the main shoe type for an activity.
    Usually the activity_item_rules table will store repeated shoe_type
    for the same act_type (e.g., class → sneaker, meet → formal).
    We take the first non-null shoe_type as the default.
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
    Given an activity type + the shoe the user is wearing,
    return item_name → score mapping.

    Rules used:
    - act_type must match
    - rule.shoe_type == shoe_type → eligible
    - rule.shoe_type is NULL → general rule (eligible regardless of shoe)
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
    Core recommendation logic.

    Steps:
    ------
    1. Determine the current event and next event from user's future schedule.
    2. Determine default shoe types for both events from activity_item_rules.
    3. Compare:
         if user_wearing_shoe == next_event_shoe
         and user_wearing_shoe != current_event_shoe → merge next event
    4. Collect items from rules (act_type + shoe_type filtering).
    5. Merge scores and sort items by importance.

    Returns:
    --------
    (current_event, next_event_or_None, sorted_item_list)
    """
    if current_time is None:
        current_time = datetime.utcnow()

    # Step 1: Find nearest two upcoming events
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

    # Step 2: Determine default shoe types for the events
    current_shoe = (
        _get_main_shoe_for_act(db, current_event.act_type)
        if current_event.act_type
        else None
    )

    include_next = False
    next_shoe = None

    if next_event and next_event.act_type:
        next_shoe = _get_main_shoe_for_act(db, next_event.act_type)

        # Key logic:
        # If user's actual shoe == next_event shoe AND differs from current_event shoe
        # → user probably will continue directly to next_event
        if next_shoe and shoe_type == next_shoe and shoe_type != current_shoe:
            include_next = True

    # Step 3: Get items for current event
    scores: Dict[str, int] = {}
    if current_event.act_type:
        cur_scores = _get_items_for_event(db, current_event.act_type, shoe_type)
        for name, sc in cur_scores.items():
            scores[name] = scores.get(name, 0) + sc

    # Step 4: Merge next event if needed
    if include_next and next_event and next_event.act_type:
        next_scores = _get_items_for_event(db, next_event.act_type, shoe_type)
        for name, sc in next_scores.items():
            scores[name] = scores.get(name, 0) + sc
    else:
        next_event = None

    # Step 5: Sort items by priority
    sorted_items = [
        name for name, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    ]

    return current_event, next_event, sorted_items
