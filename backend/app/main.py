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
    from .query import query_resume, query_job_description

    try:
        resume = query_resume(name)
        job_description = query_job_description(name)[2] # last item in tuple
        resume = " ".join(resume)
        score = score_resume(job_description, resume)
        return {
            "name": name,
            "score": score
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="JD/Resume not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

