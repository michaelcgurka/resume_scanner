from .resume_parser import parse_resume_pdf
from .insert_resume_data import insert_resume
from fastapi import FastAPI, UploadFile, File
import shutil
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)



    try:
        parsed_resume = parse_resume_pdf(file_path)

        if not parsed_resume:
            return {"error": "Unable to parse resume."}
    
        resume = insert_resume(parsed_resume)


    except Exception as e:
        print("Error parsing resume: ", e)
        return {"error": "Failed to process resume", "details": str(e)}
    
    finally:
        os.remove(file_path)

    return {"name": parsed_resume['name'], "parsed": parsed_resume, "filename": file.filename, "status": "uploaded", "db_id": resume.id}
    
