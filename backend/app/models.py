from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text


Base = declarative_base()


class Resume(Base):
    __tablename__ = "resume_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    education = Column(Text, nullable=False)
    experience = Column(Text, nullable=False)
    projects = Column(Text, nullable=False)
    skills = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)

class Job(Base):
    __tablename__ = "job_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    job_description = Column(Text, nullable=True)


