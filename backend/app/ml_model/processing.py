import re

from app.query import query_resume
from app.query import query_job_description


class PreprocessResume:

    def __init__(self, name):
        self.name = name

    def pull_resume(self):
        resume = query_resume(self.name)
        return resume
    
    def pull_job_description(self):
        job_description = query_job_description(self.name)
        return job_description
    
    def clean_resume_characters(self, resume):
        new_resume = []
        for section in resume:
            if not section:
                continue
            cleaned_section = re.sub(r"-\n", "", str(section))
            cleaned_section = re.sub(r"\n", " ", cleaned_section)
            cleaned_section = re.sub(r"\|", ",", cleaned_section)
            cleaned_section = re.sub(r"•", "", cleaned_section)
            cleaned_section = cleaned_section.replace("–", "-").replace("—", "-")
            cleaned_section = cleaned_section.replace("“", '"').replace("”", '"').replace("’", "'")
            # Remove URLS like LinkedIn or GitHub
            cleaned_section = re.sub(r"https?://\S+|www\.\S+", "", cleaned_section)
            cleaned_section = cleaned_section.replace(".", "").replace(",", "")
            cleaned_section = re.sub(r"\s+", " ", cleaned_section).strip()
            new_resume.append(cleaned_section)

        return new_resume
    
    def clean_job_description(self, job_description):
        new_job_description = []
        if not job_description:
            return
        cleaned = re.sub("", "", str(job_description))
        return new_job_description
    
