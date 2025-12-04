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

# 若資料表不存在就建立（已存在時不會改結構）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Carry Helper Demo API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 開放所有來源（必要時可縮限）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 取得 DB session 的依賴
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
    """
    建立新使用者：
    - body: { "user_name": "Alice" }
    - user_id 由資料庫 sequence 自動產生
    """
    return crud.create_user(db, user_in)


@app.get("/users/", response_model=list[schemas.UserRead])
def read_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    取得使用者列表（可分頁）
    """
    return crud.list_users(db, skip, limit)


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    以 user_id（對外識別用）取得單一使用者
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# =====================
# Events
# =====================

@app.post("/events/", response_model=schemas.EventRead)
def create_event(ev_in: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    建立事件：
    - 會先檢查 ev_in.user_id 是否為有效使用者
    """
    if not crud.get_user(db, ev_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_event(db, ev_in)


@app.get("/events/", response_model=list[schemas.EventRead])
def read_events(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    取得所有事件列表
    """
    return crud.list_events(db, skip, limit)


@app.get("/events/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    取得單一事件
    """
    ev = crud.get_event(db, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev


@app.get("/users/{user_id}/events", response_model=list[schemas.EventRead])
def list_user_events(user_id: int, db: Session = Depends(get_db)):
    """
    取得特定使用者的所有事件（以 users.user_id 查）
    """
    return crud.list_events_for_user(db, user_id)


# =====================
# Event Items
# =====================

@app.post("/event_items/", response_model=schemas.EventItemRead)
def create_event_item(
    item_in: schemas.EventItemCreate, db: Session = Depends(get_db)
):
    """
    建立事件所需物品：
    - 會先檢查 event 是否存在
    - user_id / user_name 建議在 crud 中依據 event 自動補上
    """
    if not crud.get_event(db, item_in.event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.create_event_item(db, item_in)


@app.get("/event_items/", response_model=list[schemas.EventItemRead])
def read_event_items(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    取得所有事件物品
    """
    return crud.list_event_items(db, skip, limit)


@app.get("/event_items/{item_id}", response_model=schemas.EventItemRead)
def get_event_item(item_id: int, db: Session = Depends(get_db)):
    """
    取得單一事件物品
    """
    item = crud.get_event_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/events/{event_id}/items", response_model=list[schemas.EventItemRead])
def list_items_for_event(event_id: int, db: Session = Depends(get_db)):
    """
    取得某事件底下的物品清單
    """
    return crud.list_items_for_event(db, event_id)


# =====================
# Reminder Logs
# =====================

@app.post("/reminder_logs/", response_model=schemas.ReminderLogRead)
def create_reminder_log(
    r_in: schemas.ReminderLogCreate, db: Session = Depends(get_db)
):
    """
    建立提醒紀錄：
    - 會先檢查 user 是否存在（以 users.user_id）
    - user_name 建議在 crud 中依 user_id 查出後寫入
    """
    if not crud.get_user(db, r_in.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_reminder_log(db, r_in)


@app.get("/reminder_logs/", response_model=list[schemas.ReminderLogRead])
def read_reminder_logs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    取得所有提醒紀錄
    """
    return crud.list_reminder_logs(db, skip, limit)


@app.get("/reminder_logs/{log_id}", response_model=schemas.ReminderLogRead)
def get_reminder_log(log_id: int, db: Session = Depends(get_db)):
    """
    取得單一提醒紀錄
    """
    log = crud.get_reminder_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Reminder log not found")
    return log


@app.get("/users/{user_id}/reminders", response_model=list[schemas.ReminderLogRead])
def list_reminders_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    取得某使用者的所有提醒紀錄（以 users.user_id 查）
    """
    return crud.list_reminders_for_user(db, user_id)