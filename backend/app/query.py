import psycopg2
from dotenv import load_dotenv
import os

def query_resume(name):

    load_dotenv()

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    cur = conn.cursor()
    query = f"SELECT * FROM resume_info where name = '{name}';"
    print(query)
    cur.execute(query)
    resume = cur.fetchall()
    
    # TODO: fix handling of multiple resumes
    if len(resume) > 1:
        resume = resume[-1]

    return resume[0] # return as tuple

