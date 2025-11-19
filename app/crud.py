# crud.py
from sqlalchemy.orm import Session
import app.models as models, app.schemas as schemas

# users
def create_user(db: Session, user_in: schemas.UserCreate):
    db_user = models.User(name=user_in.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# events
def create_event(db: Session, ev_in: schemas.EventCreate):
    db_ev = models.Event(
        user_id=ev_in.user_id,
        title=ev_in.title,
        location=ev_in.location,
        start_time=ev_in.start_time,
        end_time=ev_in.end_time
    )
    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)
    return db_ev

def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def list_events_for_user(db: Session, user_id: int):
    return db.query(models.Event).filter(models.Event.user_id == user_id).order_by(models.Event.start_time).all()

# event_items
def create_event_item(db: Session, item_in: schemas.EventItemCreate):
    db_item = models.EventItem(
        event_id=item_in.event_id,
        item_name=item_in.item_name,
        is_required=item_in.is_required
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def list_items_for_event(db: Session, event_id: int):
    return db.query(models.EventItem).filter(models.EventItem.event_id == event_id).all()

# reminder logs
def create_reminder_log(db: Session, r_in: schemas.ReminderLogCreate):
    db_log = models.ReminderLog(
        user_id=r_in.user_id,
        event_id=r_in.event_id,
        reminder_text=r_in.reminder_text,
        triggered_by=r_in.triggered_by
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def list_reminders_for_user(db: Session, user_id: int):
    return db.query(models.ReminderLog).filter(models.ReminderLog.user_id == user_id).order_by(models.ReminderLog.created_at.desc()).all()
