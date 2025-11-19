# init_db.py
from app.database import Base, engine
from app.models import *

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully!")
