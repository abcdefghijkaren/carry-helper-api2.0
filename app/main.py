# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import app.models as models, app.schemas as schemas, crud
from database import SessionLocal, engine
from dotenv import load_dotenv
import os

load_dotenv()

# create tables if not exist (for demo)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Outfit Reminder Demo API")

# CORS - allow your frontend origin (示範開放所有，部署時請改為具體 domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo 用 "*"，正式請改成你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root
@app.get("/")
def root():
    return {"status": "ok"}

# Users
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

# Events
@app.post("/events/", response_model=schemas.EventRead)
def create_event(ev_in: schemas.EventCreate, db: Session = Depends(get_db)):
    # basic validation: check user exists
    if not crud.get_user(db, ev_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_event(db, ev_in)

@app.get("/users/{user_id}/events", response_model=list[schemas.EventRead])
def list_user_events(user_id: int, db: Session = Depends(get_db)):
    return crud.list_events_for_user(db, user_id)

@app.get("/events/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = crud.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev

# Event items
@app.post("/event_items/", response_model=schemas.EventItemRead)
def create_event_item(item_in: schemas.EventItemCreate, db: Session = Depends(get_db)):
    # check event exists
    if not crud.get_event(db, item_in.event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.create_event_item(db, item_in)

@app.get("/events/{event_id}/items", response_model=list[schemas.EventItemRead])
def list_items(event_id: int, db: Session = Depends(get_db)):
    return crud.list_items_for_event(db, event_id)

# Reminder logs
@app.post("/reminder_logs/", response_model=schemas.ReminderLogRead)
def create_reminder(r_in: schemas.ReminderLogCreate, db: Session = Depends(get_db)):
    # quick validation
    if not crud.get_user(db, r_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_reminder_log(db, r_in)

@app.get("/users/{user_id}/reminders", response_model=list[schemas.ReminderLogRead])
def list_reminders(user_id: int, db: Session = Depends(get_db)):
    return crud.list_reminders_for_user(db, user_id)
