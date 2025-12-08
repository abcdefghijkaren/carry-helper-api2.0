# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
import app.crud as crud
from app.database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carry Helper Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
# Event Items
# =====================

@app.post("/event_items/", response_model=schemas.EventItemRead)
def create_event_item(item_in: schemas.EventItemCreate, db: Session = Depends(get_db)):
    if not crud.get_event(db, item_in.event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.create_event_item(db, item_in)


@app.get("/event_items/", response_model=list[schemas.EventItemRead])
def read_event_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_event_items(db, skip, limit)


@app.get("/event_items/{item_id}", response_model=schemas.EventItemRead)
def get_event_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_event_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/events/{event_id}/items", response_model=list[schemas.EventItemRead])
def list_items_for_event(event_id: int, db: Session = Depends(get_db)):
    return crud.list_items_for_event(db, event_id)


# =====================
# Reminder Logs
# =====================

@app.post("/reminder_logs/", response_model=schemas.ReminderLogRead)
def create_reminder_log(r_in: schemas.ReminderLogCreate, db: Session = Depends(get_db)):
    if not crud.get_user(db, r_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_reminder_log(db, r_in)


@app.get("/reminder_logs/", response_model=list[schemas.ReminderLogRead])
def read_reminder_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_reminder_logs(db, skip, limit)


@app.get("/reminder_logs/{log_id}", response_model=schemas.ReminderLogRead)
def get_reminder_log(log_id: int, db: Session = Depends(get_db)):
    log = crud.get_reminder_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Reminder log not found")
    return log


@app.get("/users/{user_id}/reminders", response_model=list[schemas.ReminderLogRead])
def list_reminders_for_user(user_id: int, db: Session = Depends(get_db)):
    return crud.list_reminders_for_user(db, user_id)


# =====================
# Recommendations
# =====================

@app.post("/recommendations/", response_model=schemas.RecommendResponse)
def get_recommendations(
    req: schemas.RecommendRequest,
    db: Session = Depends(get_db),
):
    # 確認使用者存在
    if not crud.get_user(db, req.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    current_event, next_event, items = crud.infer_recommendations(
        db=db,
        user_id=req.user_id,
        shoe_type=req.shoe_type,
        current_time=req.current_time,
    )

    return schemas.RecommendResponse(
        current_event=current_event,
        next_event=next_event,
        items=items,
    )
