import streamlit as st
import requests
import PyPDF2
import docx2txt

# -----------------------
# Helper Functions
# -----------------------
def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text.lower()
    elif file.name.endswith(".docx"):
        return docx2txt.process(file).lower()
    return ""

# -----------------------
# Student Dashboard
# -----------------------
st.title("👨‍🎓 Student Dashboard")

if st.session_state.get('role') != 'Student':
    st.warning("You must log in as a Student!")
    st.stop()

st.write(f"Logged in as: {st.session_state.get('username')}")

# Resume uploader
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
if resume_file:
    if st.button("Upload Resume"):
        check_resp = requests.post(
            "http://127.0.0.1:8000/check_resume/",
            files={"file": resume_file}
        ).json()

        if check_resp.get("exists"):
            st.warning("This resume already exists. Overwrite?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Overwrite", key="overwrite_resume_yes"):
                    requests.post(
                        "http://127.0.0.1:8000/upload_resume/",
                        files={"file": resume_file},
                        data={"overwrite": "true"}
                    )
                    st.success("Resume overwritten successfully ✅")
            with col2:
                if st.button("No, Cancel", key="overwrite_resume_no"):
                    st.info("Upload canceled ❌")
        else:
            requests.post("http://127.0.0.1:8000/upload_resume/", files={"file": resume_file})
            st.success("Resume uploaded successfully ✅")
    