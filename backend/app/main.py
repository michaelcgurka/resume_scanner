from .resume_parser import parse_resume_pdf
from .insert_resume_data import insert_resume
from .scoring_logic import score_resume
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
import shutil
from fastapi.middleware.cors import CORSMiddleware
import os
from .query import query_resume, query_job_description

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), description: str = Form(...)):

    contents = await file.read()
    
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(contents)


    try:
        parsed_resume = parse_resume_pdf(file_path)

        if parsed_resume:
            resume = insert_resume(parsed_resume)
        else:
            return {
                "filename": file.filename,
                "status": "failed",
                "error": "Unable to parse resume."
            }

    except Exception as e:
        print("Error parsing resume: ", e)
        return {"error": "Failed to process resume", "details": str(e)}
    
    finally:
        os.remove(file_path)

    return {"name": parsed_resume['name'], "parsed": parsed_resume, "filename": file.filename, "status": "uploaded", "db_id": resume.id}
    

@app.post("/score_resume/{name}")
async def score_resume_endpoint(name: str):
    try:
        resume = query_resume(name)
        job_description = query_job_description(name)

        score = score_resume(job_description, resume)
        return {
            "name": name,
            "score": score
        }
    except IndexError:
        raise HTTPException(status_code=404, detail="JD/Resume not found.")
    except Exception as e:
        HTTPException(status_code=500, detail=str(e))