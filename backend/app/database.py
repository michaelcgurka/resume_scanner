from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Use PostgreSQL if all DB_* are set (e.g. on Render); otherwise SQLite for local dev
if DB_NAME and DB_HOST and DB_USER:
    DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD or ''}@{DB_HOST}:{DB_PORT or '5432'}/{DB_NAME}"
else:
    _here = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(os.path.dirname(_here))
    _sqlite_path = os.path.join(_root, "local.db")
    DB_URL = f"sqlite:///{_sqlite_path}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if "sqlite" in DB_URL:
    from .models import Base
    Base.metadata.create_all(bind=engine)
