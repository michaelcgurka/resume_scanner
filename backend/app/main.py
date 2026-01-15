from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), description: str = Form(...)):
    from .resume_parser import parse_resume_pdf
    from .insert_resume_data import insert_resume, insert_job_description, update_score
    from .scoring_logic import score_resume, resume_to_string

    contents = await file.read()
    
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(contents)


    try:
        parsed_resume = parse_resume_pdf(file_path)

        if parsed_resume:
            resume_obj = insert_resume(parsed_resume)
            print("Successfully inserted resume.")
            job_description = insert_job_description(parsed_resume["name"], description)
            print("Successfully inserted job description.")
            name = parsed_resume["name"]
            resume = resume_to_string(resume_obj)
            score = score_resume(description, resume)
            update_score(resume_obj.id, score)
            print("Successfully scored resume.")

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

    return {"name": parsed_resume['name'], "parsed": parsed_resume, "filename": file.filename, "status": "uploaded", "db_id": resume_obj.id, "score": score}
    

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

