from .models import Resume, Job
from .database import SessionLocal

def insert_resume(resume_data: dict, description: str):
    db = SessionLocal()
    new_resume = Resume(**resume_data)
    name = new_resume.name
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    new_jd = Job(name=name, job_description=description)
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)
    db.close()

    result = {
        "resume_id": new_resume.id,
        "resume_name": new_resume.name,
        "job_id": new_jd.id,
        "job_name": new_jd.name
    }
    return result

