import streamlit as st
import requests
import PyPDF2
import docx2txt

# =======================
# Helper Functions
# =======================
def extract_text(file):
    """Extract text from PDF or DOCX"""
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
    # For demo purpose, you can enhance this later
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
# Page Config
# =======================
st.set_page_config(page_title="Automated Resume Relevance Check", layout="wide")
st.title("📄 Automated Resume Relevance Check System")

# =======================
# Login Form
# =======================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        USERS = {
            "student1": {"password": "student123", "role": "Student"},
            "placement1": {"password": "placement123", "role": "Placement Team"},
        }
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.success(f"Logged in as {user['role']} ({username})")
        else:
            st.error("Invalid username or password")
    st.stop()

# =======================
# Logout
# =======================
if st.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()

st.write(f"Logged in as: {st.session_state['role']} ({st.session_state['username']})")

# =======================
# Student Dashboard
# =======================
if st.session_state["role"] == "Student":
    st.subheader("👨‍🎓 Student Dashboard")
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

    if st.button("Upload Resume") and resume_file:
        # Send file to backend with username
        files = {"file": (resume_file.name, resume_file.getvalue())}
        data = {"username": st.session_state["username"]}
        resp = requests.post("http://127.0.0.1:8000/upload_resume/", files=files, data=data).json()

        if "warning" in resp:
            st.warning(resp["warning"])
            overwrite = st.radio("Do you want to overwrite it?", ["Yes", "No"])
            if overwrite == "Yes":
                data["overwrite"] = "true"
                resp2 = requests.post("http://127.0.0.1:8000/upload_resume/", files=files, data=data).json()
                st.success(resp2.get("message", "Resume overwritten successfully"))
        else:
            st.success(resp.get("message", "Resume uploaded successfully!"))

# =======================
# Placement Team Dashboard
# =======================
elif st.session_state["role"] == "Placement Team":
    st.subheader("🧑‍💼 Placement Team Dashboard")

    # Upload JD
    jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
    if st.button("Upload JD") and jd_file:
        files = {"file": (jd_file.name, jd_file.getvalue())}
        resp = requests.post("http://127.0.0.1:8000/upload_jd/", files=files).json()

        if "warning" in resp:
            st.warning(resp["warning"])
            overwrite = st.radio("Do you want to overwrite it?", ["Yes", "No"])
            if overwrite == "Yes":
                resp2 = requests.post("http://127.0.0.1:8000/upload_jd/", files=files, data={"overwrite": "true"}).json()
                st.success(resp2.get("message", "JD overwritten successfully"))
        else:
            st.success(resp.get("message", "JD uploaded successfully"))

    # Show Uploaded Resumes
    if st.button("Show Uploaded Resumes"):
        resp = requests.get("http://127.0.0.1:8000/resumes/").json()
        if not resp:
            st.info("No resumes uploaded yet by students.")
        for r in resp:
            st.write(f"**Candidate:** {r['candidate_name']}")
            st.write(f"File: {r['filename']}")
            st.write(f"Preview: {r['raw_text'][:200]}")
            st.markdown("---")

    # Evaluate Resumes
    if st.button("Evaluate Resumes"):
        # For simplicity, evaluate against first uploaded JD
        jds = requests.get("http://127.0.0.1:8000/jds/").json()
        if not jds:
            st.warning("No JD uploaded yet.")
        else:
            jd_text = jds[0]["raw_text"]
            jd_keywords = parse_jd_keywords(jd_text)

            resp = requests.get("http://127.0.0.1:8000/resumes/").json()
            for r in resp:
                resume_text = r["raw_text"]
                result = evaluate_resume(jd_text, resume_text, jd_keywords)

                st.write(f"**Candidate:** {r['candidate_name']}")
                st.write("**Missing Skills:**", result["missing_skills"])
                st.write("**Missing Projects:**", result["missing_projects"])
                st.write("**Missing Certifications:**", result["missing_certifications"])
                st.write("**Verdict:**", result["verdict"])
                st.markdown("---")
