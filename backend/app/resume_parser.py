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
    sections['name'] = name

    keys = list(sections.keys())

    resume_dict = {}
    resume_dict['name'] = name
    if sections['name']:
        resume_dict['education'] = sections['education']
    if 'experience' in keys:
        resume_dict['experience'] = sections['experience']
    if 'projects' in keys:
        resume_dict['projects'] = sections['projects']
    if 'skills' in keys:
        resume_dict['skills'] = sections['skills']
    if 'objective' in keys:
        resume_dict['objective'] = sections['objective']
    if 'certifications' in keys:
        resume_dict['certifications'] = sections['certifications']
    
    return resume_dict
