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

# Weights: semantic (NLP) + keyword coverage + structure completeness
W_SEMANTIC = 0.60
W_KEYWORD = 0.30
W_STRUCTURE = 0.10

# Section weights for semantic score (when resume object is provided)
# Skills and experience matter most; education and projects next; objective/certs a little.
SECTION_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.35,
    "education": 0.10,
    "projects": 0.15,
    "other": 0.05,
}

"""
Extensive list of all tech keywords related to technical roles.
"""
TECH_KEYWORDS = tech_keywords

"""
Build automaton for fast keyword search. Keywords are stored lowercase for case-insensitive matching.
"""
A = ahocorasick.Automaton()
for idx, key in enumerate(tech_keywords):
    A.add_word(key.lower(), (idx, key.lower()))
A.make_automaton()


def _extract_keywords(text: str) -> set:
    """Extract tech keywords found in text. Uses lowercase for case-insensitive match."""
    if not (text and text.strip()):
        return set()
    lower = text.lower()
    return set(v for _, v in A.iter(lower))


def _keyword_coverage(job_description: str, resume: str) -> float:
    """
    Fraction of job-description keywords that appear in the resume.
    Measures how well the resume covers what the job asks for.
    """
    jd_kw = _extract_keywords(job_description)
    resume_kw = _extract_keywords(resume)
    if not jd_kw:
        return 0.0
    return len(resume_kw & jd_kw) / len(jd_kw)


def _structure_score(resume) -> float:
    """
    Bonus for having key sections (skills, experience, education).
    Returns 0.0 to 1.0; we scale by W_STRUCTURE in the final score.
    """
    if hasattr(resume, "skills") and hasattr(resume, "experience") and hasattr(resume, "education"):
        n = sum(1 for attr in (resume.skills, resume.experience, resume.education) if attr and str(attr).strip())
        return n / 3.0
    return 0.0


def resume_to_sections(resume) -> dict:
    """Build a dict of section name -> text for section-weighted scoring. Only non-empty sections."""
    sections = {}
    if getattr(resume, "skills", None) and str(resume.skills).strip():
        sections["skills"] = str(resume.skills).strip()
    if getattr(resume, "experience", None) and str(resume.experience).strip():
        sections["experience"] = str(resume.experience).strip()
    if getattr(resume, "education", None) and str(resume.education).strip():
        sections["education"] = str(resume.education).strip()
    if getattr(resume, "projects", None) and str(resume.projects).strip():
        sections["projects"] = str(resume.projects).strip()
    other_parts = []
    if getattr(resume, "objective", None) and str(resume.objective).strip():
        other_parts.append(str(resume.objective).strip())
    if getattr(resume, "certifications", None) and str(resume.certifications).strip():
        other_parts.append(str(resume.certifications).strip())
    if other_parts:
        sections["other"] = " ".join(other_parts)
    return sections


def _section_weighted_semantic(model, job_description: str, sections: dict) -> float:
    """
    Embed the JD once; embed each resume section; compute weighted average of cosine similarities.
    Sections not present get weight redistributed proportionally among present ones.
    """
    jd_emb = model.encode(job_description)
    total = 0.0
    weight_used = 0.0
    for name, weight in SECTION_WEIGHTS.items():
        if name not in sections or not sections[name]:
            continue
        text = sections[name]
        if not text.strip():
            continue
        sec_emb = model.encode(text)
        sim = util.cos_sim(jd_emb, sec_emb).item()
        total += weight * sim
        weight_used += weight
    if weight_used <= 0:
        return 0.0
    # Normalize so missing sections don't penalize (we only score what we have)
    return total / weight_used


def _full_doc_semantic(model, job_description: str, resume_text: str) -> float:
    """Single embedding for JD and full resume; return cosine similarity."""
    jd_emb = model.encode(job_description)
    resume_emb = model.encode(resume_text)
    return util.cos_sim(jd_emb, resume_emb).item()


def score_resume(job_description: str, resume):
    """
    Score how well a resume matches a job description.

    resume: Either a string (full resume text) or an ORM-like object with .skills, .experience,
            .education, .projects, .objective, .certifications. If an object is passed,
            section-weighted semantic scoring is used (skills and experience weighted highest).
    Returns a float in [0, 1] (e.g. 0.85 for 85% match).
    """
    model = _get_model()
    t0 = time.perf_counter()

    # Full resume text for keyword matching (and fallback semantic)
    if hasattr(resume, "skills") or hasattr(resume, "experience"):
        resume_text = resume_to_string(resume)
    else:
        resume_text = str(resume) if resume else ""

    # 1) Semantic score: section-weighted if we have sections, else full-doc
    if hasattr(resume, "skills") or hasattr(resume, "experience"):
        sections = resume_to_sections(resume)
        if sections:
            semantic = _section_weighted_semantic(model, job_description, sections)
        else:
            semantic = _full_doc_semantic(model, job_description, resume_text) if resume_text else 0.0
    else:
        semantic = _full_doc_semantic(model, job_description, resume_text) if resume_text else 0.0

    # 2) Keyword coverage: fraction of JD keywords that appear in resume (case-insensitive)
    keyword = _keyword_coverage(job_description, resume_text)

    # 3) Structure: bonus for having skills, experience, education sections
    if hasattr(resume, "skills") and hasattr(resume, "experience") and hasattr(resume, "education"):
        structure = _structure_score(resume)
    else:
        structure = 0.0

    final = (W_SEMANTIC * semantic) + (W_KEYWORD * keyword) + (W_STRUCTURE * structure)
    elapsed = time.perf_counter() - t0
    print(f"Encode + score done in {elapsed:.1f}s (semantic={semantic:.3f} keyword={keyword:.3f} structure={structure:.3f})", flush=True)
    return round(final, 4)


"""Converts a resume from SQLAlchemy model to a single string (all sections concatenated)."""
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
