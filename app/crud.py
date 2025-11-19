# crud.py
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas

# Demo: 取得所有使用者
def get_users(db: Session):
    return db.query(models.User).all()

# Demo: 建立使用者
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
