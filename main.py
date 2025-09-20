from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import os, shutil, traceback
from database import JobDescription, SessionLocal, Resume
from utils.parser import extract_text_from_pdf, extract_text_from_docx, clean_text

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# Upload Resume Endpoint
# ------------------------------
@app.post("/upload_resume/")
async def upload_resume(
    file: UploadFile = File(...),
    username: str = Form(...),
    overwrite: bool = Form(False),
    db: Session = Depends(get_db)
):
    try:

        if not username:
            return JSONResponse(status_code=400, content={"error": "Username required"})

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        if file.filename.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_path)
        elif file.filename.endswith(".docx"):
            raw_text = extract_text_from_docx(file_path)
        else:
            return JSONResponse(status_code=400, content={"error": "Only PDF and DOCX supported"})

        clean = clean_text(raw_text)

        # Check if student already has a resume
        existing_resume = db.query(Resume).filter_by(username=username).first()

        if existing_resume:
            if overwrite:
                existing_resume.raw_text = clean
                existing_resume.filename = file.filename
                db.commit()
                db.refresh(existing_resume)
                return {
                    "message": f"{username}'s resume overwritten successfully.",
                    "preview": clean[:200],
                    "relevance_score": existing_resume.relevance_score,
                    "verdict": existing_resume.verdict
                }
            else:
                return {
                    "warning": f"{username} already has a resume uploaded.",
                    "message": "Uploading again will overwrite the existing data.",
                    "existing_preview": existing_resume.raw_text[:200]
                }

        # Insert new resume
        new_resume = Resume(
            username=username,
            candidate_name=file.filename,
            filename=file.filename,
            raw_text=clean,
            relevance_score=None,  # placeholder
            verdict=None           # placeholder
        )
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)

        return {
            "id": new_resume.id,
            "candidate_name": new_resume.candidate_name,
            "preview": clean[:200],
            "relevance_score": new_resume.relevance_score,
            "verdict": new_resume.verdict
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )


@app.post("/upload_jd/")
async def upload_jd(file: UploadFile = File(...), overwrite: bool = False, db: Session = Depends(get_db)):
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
        if overwrite:
            existing_jd.raw_text = clean
            db.commit()
            db.refresh(existing_jd)
            return {"message": f"JD '{title}' overwritten.", "preview": clean[:200]}
        else:
            return {
                "warning": f"JD '{title}' already exists.",
                "message": "Uploading again will overwrite the existing data.",
                "existing_preview": existing_jd.raw_text[:200]
            }

    # Insert new JD
    new_jd = JobDescription(title=title, raw_text=clean)
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)

    return {"id": new_jd.id, "title": new_jd.title, "preview": clean[:200]}


@app.get("/resumes/")
def get_resumes(db: Session = Depends(get_db)):
    try:
        resumes = db.query(Resume).all()
        result = []
        for r in resumes:
            result.append({
                "id": r.id,
                "candidate_name": r.candidate_name,
                "username": r.username,
                "filename": r.filename,
                "preview": r.raw_text[:200] if r.raw_text else "",
                "relevance_score": r.relevance_score,
                "verdict": r.verdict
            })
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

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
