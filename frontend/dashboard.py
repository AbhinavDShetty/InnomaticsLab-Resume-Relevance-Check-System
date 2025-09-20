import streamlit as st
import requests

st.title("📄 Automated Resume Relevance Check System")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])

# Upload Resume
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

if st.button("Upload Files"):
    if jd_file:
        resp = requests.post("http://127.0.0.1:8000/upload_jd/", files={"file": jd_file})
        st.write("JD Upload:", resp.json())

    if resume_file:
        resp = requests.post("http://127.0.0.1:8000/upload_resume/", files={"file": resume_file})
        st.write("Resume Upload:", resp.json())
