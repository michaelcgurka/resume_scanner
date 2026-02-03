"""
One-time migration: add resume_id and score to job_info.
Run from repo root: python backend/migrate_job_columns.py
Safe to run multiple times (skips if columns exist).
"""
import os
import sys

# Load .env from repo root when run as python backend/migrate_job_columns.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import psycopg2

def main():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
    conn.autocommit = True
    cur = conn.cursor()
    for col, defn in [
        ("resume_id", "INTEGER REFERENCES resume_info(id)"),
        ("score", "FLOAT"),
    ]:
        try:
            cur.execute(f"ALTER TABLE job_info ADD COLUMN {col} {defn};")
            print(f"Added column {col}.")
        except psycopg2.Error as e:
            if "already exists" in str(e) or "duplicate_column" in str(e):
                print(f"Column {col} already exists; skip.")
            else:
                raise
    print("Migration done.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
