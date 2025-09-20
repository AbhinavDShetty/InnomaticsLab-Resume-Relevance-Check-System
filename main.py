from fastapi import FastAPI, UploadFile, File, Depends
import os, shutil
from sqlalchemy.orm import Session
from database import SessionLocal, Resume, JobDescription
from utils.parser import extract_text_from_pdf, extract_text_from_docx, clean_text
from fastapi.middleware.cors import CORSMiddleware

# App & CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
    candidate_name = file.filename  # you can replace with st.session_state['username'] from frontend

    # Check if resume already exists
    existing_resume = db.query(Resume).filter_by(candidate_name=candidate_name).first()
    if existing_resume:
        # Return a warning without creating a new row
        return {
            "warning": f"Resume for {candidate_name} already exists.",
            "message": "Uploading again will overwrite the existing data.",
            "existing_preview": existing_resume.raw_text[:200]
        }

    # Create new resume if not exists
    new_resume = Resume(candidate_name=candidate_name, filename=file.filename, raw_text=clean)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {"id": new_resume.id, "candidate_name": new_resume.candidate_name, "preview": clean[:200]}


@app.post("/upload_jd/")
async def upload_jd(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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
        return {
            "warning": f"JD '{title}' already exists.",
            "message": "Uploading again will overwrite the existing data.",
            "existing_preview": existing_jd.raw_text[:200]
        }

    new_jd = JobDescription(title=title, raw_text=clean)
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)

    return {"id": new_jd.id, "title": new_jd.title, "preview": clean[:200]}


# # Upload resume
# @app.post("/upload_resume/")
# async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     if file.filename.endswith(".pdf"):
#         raw_text = extract_text_from_pdf(file_path)
#     elif file.filename.endswith(".docx"):
#         raw_text = extract_text_from_docx(file_path)
#     else:
#         return {"error": "Only PDF and DOCX supported"}

#     clean = clean_text(raw_text)
#     new_resume = Resume(candidate_name=file.filename, filename=file.filename, raw_text=clean)
#     db.add(new_resume)
#     db.commit()
#     db.refresh(new_resume)

#     return {"id": new_resume.id, "candidate_name": new_resume.candidate_name, "preview": clean[:200]}

# # Upload JD
# @app.post("/upload_jd/")
# async def upload_jd(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     if file.filename.endswith(".pdf"):
#         raw_text = extract_text_from_pdf(file_path)
#     elif file.filename.endswith(".docx"):
#         raw_text = extract_text_from_docx(file_path)
#     else:
#         return {"error": "Only PDF and DOCX supported"}

#     clean = clean_text(raw_text)
#     new_jd = JobDescription(title=file.filename, raw_text=clean)
#     db.add(new_jd)
#     db.commit()
#     db.refresh(new_jd)

#     return {"id": new_jd.id, "title": new_jd.title, "preview": clean[:200]}
