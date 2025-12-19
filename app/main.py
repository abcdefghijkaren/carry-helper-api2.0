# app/main.py
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.crud as crud
from app.database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

# 建立資料表（若尚未存在）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carry Helper Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Demo 用先放寬，之後可收斂成指定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok"}


# =====================
# Users
# =====================

@app.post("/users/", response_model=schemas.UserRead)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user_in)


@app.get("/users/", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_users(db, skip, limit)


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# =====================
# Events
# =====================

@app.post("/events/", response_model=schemas.EventRead)
def create_event(ev_in: schemas.EventCreate, db: Session = Depends(get_db)):
    if not crud.get_user(db, ev_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_event(db, ev_in)


@app.get("/events/", response_model=list[schemas.EventRead])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_events(db, skip, limit)


@app.get("/events/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = crud.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev


@app.get("/users/{user_id}/events", response_model=list[schemas.EventRead])
def list_user_events(user_id: int, db: Session = Depends(get_db)):
    return crud.list_events_for_user(db, user_id)


# =====================
# Reminders (你目前保留的 endpoint)
# =====================

@app.get("/users/{user_id}/reminders", response_model=list[schemas.ReminderLogRead])
def list_reminders_for_user(user_id: int, db: Session = Depends(get_db)):
    return crud.list_reminders_for_user(db, user_id)


# =====================
# Recommendations (GET)
# - 這裡我幫你「把朋友推薦併進 items」(不改 schema)
# =====================

@app.get("/recommendations/", response_model=schemas.RecommendResponse)
def get_recommendations(
    user_id: int,
    shoe_type: str,
    current_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    GET /recommendations/?user_id=2&shoe_type=formal
    GET /recommendations/?user_id=2&shoe_type=sneaker&current_time=2025-12-08T10:00:00Z
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_event, next_event, items = crud.infer_recommendations(
        db=db,
        user_id=user_id,
        shoe_type=shoe_type,
        current_time=current_time,
    )

    # ✅ 朋友攜帶推薦（append 到 items 最後）
    base_time = current_time or datetime.utcnow()
    friend_items = crud.get_friend_carry_recs_from_events(
        db=db,
        demo_user_id=user_id,
        current_time=base_time,
    )

    # 去重 + 保持順序（items 先、friend_items 後）
    merged = []
    for x in items:
        if x not in merged:
            merged.append(x)
    for x in friend_items:
        if x not in merged:
            merged.append(x)

    return schemas.RecommendResponse(
        current_event=current_event,
        next_event=next_event,
        items=merged,
    )


# =====================
# Detect Shoe (MCU → 後端)
# - 同樣把朋友推薦併進 items
# =====================

@app.post("/detect_shoe/")
def detect_shoe(req: schemas.ShoeDetectRequest, db: Session = Depends(get_db)):
    """
    Request body:
    {
      "user_id": 2,
      "shoe_id": 1
    }
    """
    shoe = (
        db.query(models.UserShoes)
        .filter(
            models.UserShoes.id == req.shoe_id,
            models.UserShoes.user_id == req.user_id,
        )
        .first()
    )
    if not shoe:
        raise HTTPException(status_code=404, detail="Shoe not found for this user")

    shoe_type = shoe.shoe_type

    current_event, next_event, items = crud.infer_recommendations(
        db=db,
        user_id=req.user_id,
        shoe_type=shoe_type,
        current_time=None,
    )

    # ✅ 朋友攜帶推薦（append 到 items 最後）
    base_time = datetime.utcnow()
    friend_items = crud.get_friend_carry_recs_from_events(
        db=db,
        demo_user_id=req.user_id,
        current_time=base_time,
    )

    merged = []
    for x in items:
        if x not in merged:
            merged.append(x)
    for x in friend_items:
        if x not in merged:
            merged.append(x)

    return {
        "shoe_type": shoe_type,
        "current_event": current_event,
        "next_event": next_event,
        "items": merged,
    }


# =====================
# MCU helpers
# =====================

@app.get("/mcu/common_items", response_model=schemas.CommonItemsByShoeResponse)
def mcu_common_items(
    shoe_id: int,
    db: Session = Depends(get_db)
):
    result = crud.get_common_items_by_shoe_id(db, shoe_id)
    if not result["items"]:
        raise HTTPException(status_code=404, detail="Shoe ID not found")
    return result


@app.get("/mcu/all_items", response_model=schemas.MCUAllItemsResponse)
def mcu_all_items(
    user_id: int = Query(..., description="users.user_id, demo=2"),
    shoe_id: int = Query(..., description="user_shoes.id (MCU shoe id), demo=1/2/3"),
    current_time: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """
    MCU 用 GET：
    /mcu/all_items?user_id=2&shoe_id=1
    """
    try:
        return crud.build_mcu_all_items(
            db=db,
            user_id=user_id,
            shoe_id=shoe_id,
            current_time=current_time,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =====================
# Friends carry (debug)
# =====================

@app.get("/friends-carry/{user_id}")
def list_friends_carry(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.FriendsCarryRecommendations)
        .filter(models.FriendsCarryRecommendations.user_id == user_id)
        .all()
    )
    return [{"friend_name": r.friend_name, "carry_item": r.carry_item} for r in rows]
