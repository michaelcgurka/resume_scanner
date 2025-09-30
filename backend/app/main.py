from resume_parser import parse_resume_pdf
from insert_resume_data import insert_resume

file_path = "./SWE_Resume.pdf"
parsed_resume = parse_resume_pdf(file_path=file_path)
resume = insert_resume(parsed_resume)

print(f"Successfully inserted {resume.name} with ID {resume.id}!")