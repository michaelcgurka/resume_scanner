from pdfminer.high_level import extract_text
import re


def parse_resume_pdf(file_path: str) -> dict:
    raw = extract_text(file_path)
    if not raw or not str(raw).strip():
        return None
    reader = str(raw).lower()

    deliminators = ["education", "experience", "projects", "skills", "objective", "certifications"]
    re_pattern = re.compile(r"(" + "|".join(re.escape(d) for d in deliminators) + r")", re.IGNORECASE)
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

    lines = reader.splitlines()
    name = (lines[0].strip() if lines else "Unknown") or "Unknown"

    resume_dict = {
        "name": name,
        "education": sections.get("education") or None,
        "experience": sections.get("experience") or None,
        "projects": sections.get("projects") or None,
        "skills": sections.get("skills") or None,
        "objective": sections.get("objective") or None,
        "certifications": sections.get("certifications") or None,
    }
    return resume_dict
