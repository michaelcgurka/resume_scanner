from sentence_transformers import SentenceTransformer, util
from .keyword_list import tech_keywords, KEYWORD_CATEGORIES
import ahocorasick
import time
import sys
from typing import Any, Dict, List

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


def _keyword_to_category() -> dict:
    """Build mapping keyword (lowercase) -> category name for grouping missing keywords."""
    m = {}
    for cat_name, kws in KEYWORD_CATEGORIES:
        for k in kws:
            m[k.lower()] = cat_name
    return m


_KEYWORD_CATEGORY_MAP = None


def _get_keyword_category_map():
    global _KEYWORD_CATEGORY_MAP
    if _KEYWORD_CATEGORY_MAP is None:
        _KEYWORD_CATEGORY_MAP = _keyword_to_category()
    return _KEYWORD_CATEGORY_MAP


def _get_missing_keywords(job_description: str, resume_text: str) -> list:
    """JD keywords that do not appear in the resume. Returns sorted list of lowercase keywords."""
    jd_kw = _extract_keywords(job_description)
    resume_kw = _extract_keywords(resume_text)
    missing = sorted(jd_kw - resume_kw)
    return missing


def _missing_keywords_by_category(missing_keywords: list) -> dict:
    """Group missing keywords by category. Returns dict category -> list of keywords."""
    cat_map = _get_keyword_category_map()
    by_cat = {}
    for kw in missing_keywords:
        cat = cat_map.get(kw, "Other")
        by_cat.setdefault(cat, []).append(kw)
    return by_cat


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


def _section_similarities(model, job_description: str, sections: dict) -> dict:
    """
    Per-section cosine similarity to the job description.
    Returns dict section_name -> float in [0, 1] (cos_sim can be in [-1,1]; we clamp to 0-1 for display).
    """
    jd_emb = model.encode(job_description)
    out = {}
    for name, text in sections.items():
        if not (text and str(text).strip()):
            continue
        sec_emb = model.encode(str(text).strip())
        sim = util.cos_sim(jd_emb, sec_emb).item()
        out[name] = round(max(0.0, min(1.0, sim)), 4)
    return out


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


def _generate_recommendations(
    breakdown: dict,
    missing_keywords: list,
    section_scores: dict,
    has_certifications: bool,
) -> list:
    """Rule-based actionable recommendations."""
    recs = []
    if missing_keywords:
        kw_list = ", ".join(missing_keywords[:10])
        if len(missing_keywords) > 10:
            kw_list += f", and {len(missing_keywords) - 10} more"
        recs.append(f"Add {len(missing_keywords)} missing keyword(s) from the job description: {kw_list}.")
    if breakdown.get("keyword", 1.0) < 0.5 and not missing_keywords:
        recs.append("Improve keyword alignment with the job description (consider adding relevant skills and technologies).")
    if breakdown.get("semantic", 1.0) < 0.6:
        recs.append("Strengthen the overall match to the job requirements (rephrase or add experience that aligns with the role).")
    if section_scores:
        worst = min(section_scores.items(), key=lambda x: x[1])
        if worst[1] < 0.6:
            label = worst[0].capitalize()
            recs.append(f"Strengthen the {label} section to better match the job requirements.")
    return recs


def score_resume(job_description: str, resume) -> Dict[str, Any]:
    """
    Score how well a resume matches a job description and return structured insights.

    resume: Either a string (full resume text) or an ORM-like object with .skills, .experience,
            .education, .projects, .objective, .certifications.
    Returns a dict: score, breakdown, missing_keywords, missing_keywords_by_category,
                    section_scores, recommendations.
    """
    model = _get_model()
    t0 = time.perf_counter()

    # Full resume text for keyword matching (and fallback semantic)
    if hasattr(resume, "skills") or hasattr(resume, "experience"):
        resume_text = resume_to_string(resume)
    else:
        resume_text = str(resume) if resume else ""

    sections = {}
    if hasattr(resume, "skills") or hasattr(resume, "experience"):
        sections = resume_to_sections(resume)

    # 1) Semantic score: section-weighted if we have sections, else full-doc
    if sections:
        semantic = _section_weighted_semantic(model, job_description, sections)
    else:
        semantic = _full_doc_semantic(model, job_description, resume_text) if resume_text else 0.0

    # 2) Keyword coverage
    keyword = _keyword_coverage(job_description, resume_text)

    # 3) Structure
    if hasattr(resume, "skills") and hasattr(resume, "experience") and hasattr(resume, "education"):
        structure = _structure_score(resume)
    else:
        structure = 0.0

    final = (W_SEMANTIC * semantic) + (W_KEYWORD * keyword) + (W_STRUCTURE * structure)
    final = round(final, 4)

    # Insights: missing keywords (flat + by category)
    missing_keywords = _get_missing_keywords(job_description, resume_text)
    missing_keywords_by_category = _missing_keywords_by_category(missing_keywords)

    # Section-level scores (per-section similarity to JD)
    section_scores = {}
    if sections:
        section_scores = _section_similarities(model, job_description, sections)

    # Actionable recommendations
    has_certifications = bool(
        getattr(resume, "certifications", None) and str(getattr(resume, "certifications", "") or "").strip()
    )
    recommendations = _generate_recommendations(
        {"semantic": round(semantic, 4), "keyword": round(keyword, 4), "structure": round(structure, 4)},
        missing_keywords,
        section_scores,
        has_certifications,
    )

    elapsed = time.perf_counter() - t0
    print(
        f"Encode + score done in {elapsed:.1f}s (semantic={semantic:.3f} keyword={keyword:.3f} structure={structure:.3f})",
        flush=True,
    )

    return {
        "score": final,
        "breakdown": {
            "semantic": round(semantic, 4),
            "keyword": round(keyword, 4),
            "structure": round(structure, 4),
        },
        "missing_keywords": missing_keywords,
        "missing_keywords_by_category": missing_keywords_by_category,
        "section_scores": section_scores,
        "recommendations": recommendations,
    }


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
