from models import Resume
from database import SessionLocal

def insert_resume(resume_data: dict):
    db = SessionLocal()
    new_resume = Resume(**resume_data)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    db.close()
    return new_resume


