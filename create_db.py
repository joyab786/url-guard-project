# create_db.py
import models
from database import engine

print("--- CREATING DATABASE TABLES ---")
models.Base.metadata.create_all(bind=engine)
print("--- DATABASE TABLES CREATED ---")