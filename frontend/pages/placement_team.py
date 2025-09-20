import streamlit as st
import requests
import PyPDF2
import docx2txt

# =======================
# Helper Functions
# =======================
def extract_text(file):
    """Extract text from PDF or DOCX"""
    if hasattr(file, "read"):  # Uploaded file
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
            return text.lower()
        elif file.name.endswith(".docx"):
            return docx2txt.process(file).lower()
    return ""

def parse_jd_keywords(jd_text):
    """Extract demo keywords from JD"""
    skills = ["python", "java", "machine learning", "sql"]
    projects = ["chatbot", "ecommerce website"]
    certifications = ["aws certified", "google cloud certified"]
    return {"skills": skills, "projects": projects, "certifications": certifications}

def evaluate_resume(jd_text, resume_text, jd_keywords):
    jd_skills = jd_keywords.get("skills", [])
    jd_projects = jd_keywords.get("projects", [])
    jd_certs = jd_keywords.get("certifications", [])

    missing_skills = [s for s in jd_skills if s.lower() not in resume_text]
    missing_projects = [p for p in jd_projects if p.lower() not in resume_text]
    missing_certs = [c for c in jd_certs if c.lower() not in resume_text]

    total_items = len(jd_skills + jd_projects + jd_certs)
    matched_items = total_items - len(missing_skills) - len(missing_projects) - len(missing_certs)
    score = (matched_items / total_items) * 100 if total_items > 0 else 0

    if score >= 80:
        verdict = "High"
    elif score >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"

    return {
        "missing_skills": missing_skills,
        "missing_projects": missing_projects,
        "missing_certifications": missing_certs,
        "verdict": verdict
    }

# =======================
# Placement Team Dashboard
# =======================
st.set_page_config(page_title="Placement Dashboard", layout="wide")
st.title("🧑‍💼 Placement Team Dashboard")

# Role check
if st.session_state.get('role') != 'Placement Team':
    st.warning("You must log in as Placement Team!")
    st.stop()

st.write(f"Logged in as: {st.session_state.get('username')}")

# -----------------------
# JD Upload with Overwrite Confirmation
# -----------------------
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
if st.button("Upload JD") and jd_file:
    check_resp = requests.post(
        "http://127.0.0.1:8000/check_jd/",
        files={"file": jd_file}
    ).json()

    if check_resp.get("warning"):
        with st.modal("JD Already Exists"):
            st.write(check_resp["warning"])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Overwrite", key="overwrite_yes"):
                    requests.post(
                        "http://127.0.0.1:8000/upload_jd/",
                        files={"file": jd_file},
                        data={"overwrite": "true"}
                    )
                    st.session_state['uploaded_jd'] = jd_file
                    st.success("JD overwritten successfully ✅")
            with col2:
                if st.button("No, Cancel", key="overwrite_no"):
                    st.info("Upload canceled ❌")
    else:
        requests.post("http://127.0.0.1:8000/upload_jd/", files={"file": jd_file})
        st.session_state['uploaded_jd'] = jd_file
        st.success("JD uploaded successfully ✅")

# -----------------------
# Show Uploaded Resumes
# -----------------------
if st.button("Show Uploaded Resumes"):
    resp = requests.get("http://127.0.0.1:8000/resumes/")
    if resp.status_code == 200:
        resumes = resp.json()
        if not resumes:
            st.info("No resumes uploaded yet by students.")
        for r in resumes:
            st.write(f"**{r['candidate_name']}**")
            st.write(f"Preview: {r['preview']}")
            st.markdown("---")
    else:
        st.error("Failed to fetch resumes ⚠️")

# -----------------------
# Evaluate Resumes Button
# -----------------------
if st.button("Evaluate Resumes"):
    jd_file = st.session_state.get("uploaded_jd")
    if not jd_file:
        st.warning("Please upload a JD first!")
    else:
        jd_text = extract_text(jd_file)
        jd_keywords = parse_jd_keywords(jd_text)

        resp = requests.get("http://127.0.0.1:8000/resumes/")
        if resp.status_code == 200:
            results = []
            for r in resp.json():
                resume_file = r["file"]
                resume_text = extract_text(resume_file)
                result = evaluate_resume(jd_text, resume_text, jd_keywords)
                results.append({
                    "candidate_name": r["candidate_name"],
                    "missing_skills": result["missing_skills"],
                    "missing_projects": result["missing_projects"],
                    "missing_certifications": result["missing_certifications"],
                    "verdict": result["verdict"]
                })
            st.session_state['evaluation_results'] = results
        else:
            st.error("Failed to fetch resumes for evaluation ⚠️")

# -----------------------
# Display Evaluation Results Once
# -----------------------
if 'evaluation_results' in st.session_state:
    for r in st.session_state['evaluation_results']:
        st.write(f"**Candidate:** {r['candidate_name']}")
        st.write("**Missing Skills:**", r["missing_skills"])
        st.write("**Missing Projects:**", r["missing_projects"])
        st.write("**Missing Certifications:**", r["missing_certifications"])
        st.write("**Verdict:**", r["verdict"])
        st.markdown("---")
