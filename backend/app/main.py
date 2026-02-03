from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def _safe_remove(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as e:
        print(f"Warning: could not remove temp file {path}: {e}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), description: str = Form(...)):
    from .resume_parser import parse_resume_pdf
    from .insert_resume_data import insert_resume, insert_job_description, update_score
    from .scoring_logic import score_resume, resume_to_string

    contents = await file.read()
    suffix = os.path.splitext(file.filename or "")[1] or ".pdf"
    fd, file_path = tempfile.mkstemp(suffix=suffix, prefix="resume_upload_")
    try:
        with os.fdopen(fd, "wb") as buffer:
            buffer.write(contents)
    except Exception:
        _safe_remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

    try:
        parsed_resume = parse_resume_pdf(file_path)
        if not parsed_resume:
            raise HTTPException(status_code=422, detail="Unable to parse resume.")

        resume_obj = insert_resume(parsed_resume)
        insert_job_description(parsed_resume["name"], description)
        resume_text = resume_to_string(resume_obj)
        score = score_resume(description, resume_text)
        update_score(resume_obj.id, score)

        return {
            "name": parsed_resume["name"],
            "parsed": parsed_resume,
            "filename": file.filename,
            "status": "uploaded",
            "db_id": resume_obj.id,
            "score": score,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error processing resume:", e)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}") from e
    finally:
        _safe_remove(file_path)
    

@app.post("/score_resume/{name}")
async def score_resume_endpoint(name: str):
    from .scoring_logic import score_resume
    from .query import query_resume, query_job_description, resume_row_to_text

    try:
        resume_row = query_resume(name)
        job_row = query_job_description(name)
        jd_text = job_row[2] if len(job_row) > 2 and job_row[2] else ""
        resume_text = resume_row_to_text(resume_row)
        if not resume_text.strip():
            raise HTTPException(status_code=422, detail="Resume has no text content to score.")
        if not jd_text or not str(jd_text).strip():
            raise HTTPException(status_code=422, detail="Job description is empty.")
        score = score_resume(str(jd_text), resume_text)
        return {"name": name, "score": score}
    except IndexError:
        raise HTTPException(status_code=404, detail="JD/Resume not found.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

