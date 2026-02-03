from sentence_transformers import SentenceTransformer, util
from .keyword_list import tech_keywords
import ahocorasick
import time
import sys

# Lazy-load model so backend starts fast; first score request will load it once.
_model = None

def _get_model():
    global _model
    if _model is None:
        t0 = time.perf_counter()
        print("Loading ML model (first time may download ~90MB and take 1–5+ min)...", flush=True)
        sys.stdout.flush()
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        elapsed = time.perf_counter() - t0
        print(f"Model loaded in {elapsed:.1f}s", flush=True)
    return _model

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
A.make_automaton()


"""
Contains the bulk of the resume scoring logic. This is where matching,
tokenization, embedding, etc takes place.
"""
def score_resume(job_description, resume):
    model = _get_model()
    t0 = time.perf_counter()
    jd_embedding = model.encode(job_description)
    resume_embedding = model.encode(resume)
    elapsed = time.perf_counter() - t0
    print(f"Encode + score done in {elapsed:.1f}s", flush=True)

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