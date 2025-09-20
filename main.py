from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os, shutil

from database import SessionLocal, Resume, JobDescription
from utils.parser import extract_text_from_pdf, extract_text_from_docx, clean_text

# ----------------------
# FastAPI App & CORS
# ----------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Upload Directory
# ----------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------------
# Dependency for DB
# ----------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# Upload Resume
# ----------------------
@app.post("/upload_resume/")
async def upload_resume(
    file: UploadFile = File(...),
    username: str = Form(...),
    overwrite: str = Form("false"),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    if file.filename.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        return {"error": "Only PDF and DOCX supported"}

    clean = clean_text(raw_text)

    # Check if resume exists
    existing_resume = db.query(Resume).filter_by(candidate_name=username).first()
    if existing_resume:
        if overwrite.lower() != "true":
            return {"warning": f"Resume for {username} already exists.", 
                    "message": "Uploading again will overwrite the existing data.",
                    "existing_preview": existing_resume.raw_text[:200]}
        else:
            existing_resume.filename = file.filename
            existing_resume.raw_text = clean
            db.commit()
            return {"message": f"Resume for {username} overwritten successfully!"}

    # Create new resume
    new_resume = Resume(candidate_name=username, filename=file.filename, raw_text=clean)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return {"message": f"Resume uploaded successfully for {username}!"}

# ----------------------
# Upload JD
# ----------------------
@app.post("/upload_jd/")
async def upload_jd(
    file: UploadFile = File(...),
    overwrite: str = Form("false"),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text
    if file.filename.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        return {"error": "Only PDF and DOCX supported"}

    clean = clean_text(raw_text)
    title = file.filename

    existing_jd = db.query(JobDescription).filter_by(title=title).first()
    if existing_jd:
        if overwrite.lower() != "true":
            return {"warning": f"JD '{title}' already exists.",
                    "message": "Uploading again will overwrite the existing data.",
                    "existing_preview": existing_jd.raw_text[:200]}
        else:
            existing_jd.raw_text = clean
            db.commit()
            return {"message": f"JD '{title}' overwritten successfully!"}

    # Create new JD
    new_jd = JobDescription(title=title, raw_text=clean)
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)
    return {"message": f"JD '{title}' uploaded successfully!"}

# ----------------------
# Get all resumes
# ----------------------
@app.get("/resumes/")
def get_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).all()
    return [
        {
            "candidate_name": r.candidate_name,
            "filename": r.filename,
            "raw_text": r.raw_text,
            "relevance_score": r.relevance_score,
            "verdict": r.verdict
        } for r in resumes
    ]

# ----------------------
# Get all JDs
# ----------------------
@app.get("/jds/")
def get_jds(db: Session = Depends(get_db)):
    jds = db.query(JobDescription).all()
    return [
        {"title": jd.title, "raw_text": jd.raw_text} for jd in jds
    ]
# ----------------------
# Evaluate Resumes  