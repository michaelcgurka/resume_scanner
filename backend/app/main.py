from resume_parser import parse_resume_pdf
from insert_resume_data import insert_resume
from fastapi import FastAPI, UploadFile, File
import shutil

file_path = "./SWE_Resume.pdf"
parsed_resume = parse_resume_pdf(file_path=file_path)
resume = insert_resume(parsed_resume)

print(f"Successfully inserted {resume.name} with ID {resume.id}!")

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "status": "uploaded"}
    
