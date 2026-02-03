import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def _get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def query_resume(name):
    """Return one resume row (tuple) for the given name. Raises IndexError if not found."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM resume_info WHERE name = %s;", (name,))
        rows = cur.fetchall()
        if not rows:
            raise IndexError("No resume found for name: {}".format(name))
        return max(rows, key=lambda r: r[0])
    finally:
        conn.close()


def query_job_description(name):
    """Return one job row (tuple): (id, name, job_description). Raises IndexError if not found."""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM job_info WHERE name = %s;", (name,))
        rows = cur.fetchall()
        if not rows:
            raise IndexError("No job description found for name: {}".format(name))
        return max(rows, key=lambda r: r[0])
    finally:
        conn.close()


def resume_row_to_text(row):
    """Build a single string from a resume row for scoring. Row: id, name, education, ..., score."""
    text_parts = []
    for i in range(2, 8):
        if i < len(row) and row[i] is not None and str(row[i]).strip():
            text_parts.append(str(row[i]).strip())
    return " ".join(text_parts)
