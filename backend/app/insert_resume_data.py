from .models import Resume, Job
from .database import SessionLocal


def insert_resume(resume_data: dict):
    """Insert a new resume. Prefer get_or_create_resume for one-resume-per-name flow."""
    db = SessionLocal()
    new_resume = Resume(**resume_data)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    db.close()
    return new_resume


def get_or_create_resume(resume_data: dict):
    """
    One resume per name: if a resume with this name exists, update its fields and return it.
    Otherwise insert a new resume. Returns (resume, created) where created is True if new.
    """
    db = SessionLocal()
    try:
        name = resume_data.get("name")
        existing = db.query(Resume).filter(Resume.name == name).first()
        if existing:
            for key, value in resume_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing, False
        new_resume = Resume(**resume_data)
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        return new_resume, True
    finally:
        db.close()


def insert_job(resume_id: int, name: str, job_description: str):
    """Insert a new job description linked to a resume. Returns the Job (score set separately)."""
    db = SessionLocal()
    new_job = Job(resume_id=resume_id, name=name, job_description=job_description)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    db.close()
    return new_job


def insert_job_description(name: str, job_description: str):
    """Legacy: insert job by name only (no resume_id). Prefer insert_job for new flow."""
    db = SessionLocal()
    new_job = Job(name=name, job_description=job_description)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    db.close()
    return new_job


def update_score(resume_id: int, score: float):
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume id {resume_id} not found")
        resume.score = score
        db.commit()
        db.refresh(resume)
        return resume
    except Exception as e:
        db.rollback()
        print(f"Error updating score: {e}")
        raise
    finally:
        db.close()


def update_job_score(job_id: int, score: float):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job id {job_id} not found")
        job.score = score
        db.commit()
        db.refresh(job)
        return job
    except Exception as e:
        db.rollback()
        print(f"Error updating job score: {e}")
        raise
    finally:
        db.close()


def get_resume_by_name(name: str):
    """Return the single resume for this name, or None."""
    db = SessionLocal()
    try:
        return db.query(Resume).filter(Resume.name == name).first()
    finally:
        db.close()


def get_jobs_by_resume_id(resume_id: int):
    """Return all jobs for this resume, ordered by id (newest last)."""
    db = SessionLocal()
    try:
        return db.query(Job).filter(Job.resume_id == resume_id).order_by(Job.id).all()
    finally:
        db.close()
