from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./resumes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    raw_text = Column(Text)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, index=True)
    username = Column(String, unique=True)
    filename = Column(String)
    raw_text = Column(Text)
    relevance_score = Column(Float, default=None)
    verdict = Column(String, default=None)

# Create tables
Base.metadata.create_all(bind=engine)
