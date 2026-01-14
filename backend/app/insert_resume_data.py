from .models import Resume, Job
from .database import SessionLocal

def insert_resume(resume_data: dict):
    db = SessionLocal()
    new_resume = Resume(**resume_data)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    db.close()
    return new_resume

def insert_job_description(name: str, job_description: str):
    db = SessionLocal()
    new_job = Job(name=name, job_description=job_description)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    db.close()
    return new_job


