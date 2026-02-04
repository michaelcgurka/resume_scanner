from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import tempfile
import time

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload limits (tune for production)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf"}

def _safe_remove(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as e:
        print(f"Warning: could not remove temp file {path}: {e}")


@app.get("/warmup")
async def warmup():
    """
    Preload the ML model so the first upload is fast.
    Call this when the app loads (e.g. from the frontend); the first call may take 1–5+ min
    (download + load). Subsequent uploads then only take a few seconds.
    """
    from .scoring_logic import _get_model
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _get_model)
    return {"status": "ready", "message": "Scoring model loaded."}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), description: str = Form(...)):
    from .resume_parser import parse_resume_pdf
    from .insert_resume_data import (
        get_or_create_resume,
        insert_job,
        update_score,
        update_job_score,
    )
    from .scoring_logic import score_resume, resume_to_string

    t_start = time.perf_counter()
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_BYTES // (1024*1024)} MB.",
        )
    suffix = (os.path.splitext(file.filename or "")[1] or "").lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail="Only PDF files are allowed.",
        )
    fd, file_path = tempfile.mkstemp(suffix=suffix, prefix="resume_upload_")
    try:
        with os.fdopen(fd, "wb") as buffer:
            buffer.write(contents)
    except Exception:
        _safe_remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    try:
        t0 = time.perf_counter()
        parsed_resume = parse_resume_pdf(file_path)
        print(f"Parse PDF: {time.perf_counter() - t0:.1f}s", flush=True)
        if not parsed_resume:
            raise HTTPException(status_code=422, detail="Unable to parse resume.")

        # One resume per name: reuse or create
        t0 = time.perf_counter()
        resume_obj, _ = get_or_create_resume(parsed_resume)
        job_obj = insert_job(resume_obj.id, parsed_resume["name"], description)
        print(f"DB get/create + insert job: {time.perf_counter() - t0:.1f}s", flush=True)
        t0 = time.perf_counter()
        loop = asyncio.get_event_loop()
        score = await loop.run_in_executor(None, lambda: score_resume(description, resume_obj))
        print(f"Score (model load + encode): {time.perf_counter() - t0:.1f}s", flush=True)
        update_job_score(job_obj.id, score)
        update_score(resume_obj.id, score)

        print(f"Upload total: {time.perf_counter() - t_start:.1f}s", flush=True)
        return {
            "name": parsed_resume["name"],
            "parsed": parsed_resume,
            "filename": file.filename,
            "status": "uploaded",
            "db_id": resume_obj.id,
            "job_id": job_obj.id,
            "score": score,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error processing resume:", e)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}") from e
    finally:
        _safe_remove(file_path)
    

@app.post("/resume/{name}/job")
async def add_job_description(name: str, body: dict = Body(...)):
    """Add a job description for an existing resume (by name). Returns the new job and score."""
    from .insert_resume_data import (
        get_resume_by_name,
        insert_job,
        update_job_score,
        update_score,
    )
    from .scoring_logic import score_resume

    description = body.get("description") or body.get("job_description") or ""
    if not str(description).strip():
        raise HTTPException(status_code=422, detail="description is required")

    resume = get_resume_by_name(name)
    if not resume:
        raise HTTPException(status_code=404, detail=f"No resume found for name: {name}")

    job_obj = insert_job(resume.id, name, str(description))
    loop = asyncio.get_event_loop()
    score = await loop.run_in_executor(
        None, lambda: score_resume(str(description), resume)
    )
    update_job_score(job_obj.id, score)
    update_score(resume.id, score)

    return {
        "name": name,
        "job_id": job_obj.id,
        "resume_id": resume.id,
        "score": score,
    }


@app.get("/resume/{name}/jobs")
async def list_jobs_for_resume(name: str):
    """List all job descriptions (and scores) for the resume with this name."""
    from .insert_resume_data import get_resume_by_name, get_jobs_by_resume_id

    resume = get_resume_by_name(name)
    if not resume:
        raise HTTPException(status_code=404, detail=f"No resume found for name: {name}")

    jobs = get_jobs_by_resume_id(resume.id)
    return {
        "name": name,
        "resume_id": resume.id,
        "jobs": [
            {
                "id": j.id,
                "job_description": j.job_description,
                "score": j.score,
            }
            for j in jobs
        ],
    }


@app.post("/score_resume/{name}")
async def score_resume_endpoint(name: str, job_id: int = None):
    """
    Get score for resume by name. If job_id is provided (query param), score for that job;
    otherwise use the most recent job for that name.
    """
    from .scoring_logic import score_resume
    from .insert_resume_data import get_resume_by_name, get_jobs_by_resume_id

    try:
        resume = get_resume_by_name(name)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found.")

        if job_id is not None:
            jobs = get_jobs_by_resume_id(resume.id)
            job = next((j for j in jobs if j.id == job_id), None)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found.")
            jd_text = job.job_description or ""
        else:
            jobs = get_jobs_by_resume_id(resume.id)
            if not jobs:
                raise HTTPException(status_code=404, detail="No job description found.")
            job = jobs[-1]
            jd_text = job.job_description or ""

        if not jd_text.strip():
            raise HTTPException(status_code=422, detail="Job description is empty.")

        loop = asyncio.get_event_loop()
        score = await loop.run_in_executor(
            None, lambda: score_resume(str(jd_text), resume)
        )
        return {"name": name, "job_id": job.id, "score": score}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in score_resume endpoint:", e, flush=True)
        raise HTTPException(status_code=500, detail="Scoring failed. Please try again.")

