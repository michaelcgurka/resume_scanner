from sentence_transformers import SentenceTransformer, util
from keyword_list import tech_keywords

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("I am a Python engineer skilled in machine learning")
print(embedding.shape)

"""
Extensive list of all tech keywords related to technical roles.
"""
TECH_KEYWORDS = tech_keywords

"""
Contains the bulk of the resume scoring logic. This is where matching,
tokenization, embedding, etc takes place.
"""
def score_resume(job_description, resume):

    jd_embedding = model.encode(job_description)
    resume_embedding = model.encode(resume)

    cosine_similarity = util.cos_sim(jd_embedding, resume_embedding)

    

    return
