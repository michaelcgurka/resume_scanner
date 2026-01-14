from sentence_transformers import SentenceTransformer, util
from .keyword_list import tech_keywords
import ahocorasick
from sqlalchemy import inspect

model = SentenceTransformer('all-MiniLM-L6-v2')

keyword_weight = 0.3

"""
Extensive list of all tech keywords related to technical roles.
"""
TECH_KEYWORDS = tech_keywords

"""
Build automation for keywords that will later be searched through.
"""
A = ahocorasick.Automaton()
for idx, key in enumerate(tech_keywords):
    A.add_word(key, (idx, key))
A.make_automation()


"""
Contains the bulk of the resume scoring logic. This is where matching,
tokenization, embedding, etc takes place.
"""
def score_resume(job_description, resume):

    jd_embedding = model.encode(job_description)
    resume_embedding = model.encode(resume)

    cosine_similarity = util.cos_sim(jd_embedding, resume_embedding).item()

    resume_matches = set([v[1] for _, v in A.iter(resume)])
    jd_matches = set([v[1] for _, v in A.iter(job_description)])
    
    if jd_matches:
        keyword_score = len(resume_matches & jd_matches) / len(jd_matches)
    else:
        keyword_score = 0

    final_score = (cosine_similarity * (1 - keyword_weight)) + (keyword_weight * keyword_score)
    return round(final_score, 4)


""" Converts a resume from SQLAlchemy model to a string. """
def resume_to_string(resume):
    parts = []
    if resume.education:
        parts.append(resume.education)
    if resume.experience:
        parts.append(resume.experience)
    if resume.projects:
        parts.append(resume.projects)
    if resume.skills:
        parts.append(resume.skills)
    if resume.objective:
        parts.append(resume.objective)
    if resume.certifications:
        parts.append(resume.certifications)
    return " ".join(parts)