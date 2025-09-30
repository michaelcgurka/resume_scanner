from pdfminer.high_level import extract_text
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os


def parse_resume_pdf(file_path: str) -> dict:
    reader = (extract_text(file_path)).lower()


    deliminators = ["education", "experience", "projects", "skills", "objective", "certifications"]
    re_pattern = re.compile(r"(" + "|".join(deliminators) + r")", re.IGNORECASE)

    result = re_pattern.split(reader)
    sections = {}
    key = None
    for part in result:
        if not part.strip():
            continue
        if part.lower() in deliminators: 
            key = part.lower()
            sections[key] = ""
        elif key:
            sections[key] = part.strip()





    def extract_name(text):
        name = text.splitlines()[0]
        return name
        
    name = extract_name(reader)

    resume_dict = {}
    resume_dict['name'] = name
    resume_dict['education'] = sections['education']
    resume_dict['experience'] = sections['experience']
    resume_dict['projects'] = sections['projects']
    resume_dict['skills'] = sections['skills']
    resume_dict['objective'] = sections['objective']
    resume_dict['certifications'] = None

    print(resume_dict)
    
    return resume_dict

