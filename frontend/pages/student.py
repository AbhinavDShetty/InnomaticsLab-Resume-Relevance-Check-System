import streamlit as st
import requests

st.set_page_config(page_title="Student Dashboard", layout="wide")
st.title("👨‍🎓 Student Dashboard")

# Role check
if st.session_state.get('role') != 'Student':
    st.warning("You must log in as a Student!")
    st.stop()

st.write(f"Logged in as: {st.session_state.get('username')}")

# Resume Upload
resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# if st.button("Upload Resume"):
#     if resume_file:
#         resp = requests.post(
#             "http://127.0.0.1:8000/upload_resume/",
#             files={"file": resume_file}
#         )
#         st.write(resp.json())

if st.button("Upload Resume"):
    if resume_file:
        resp = requests.post(
            "http://127.0.0.1:8000/upload_resume/",
            files={"file": resume_file}
        ).json()

        if "warning" in resp:
            st.warning(resp["warning"])
            if st.button("Overwrite existing resume?"):
                # Add extra parameter to force overwrite
                resp = requests.post(
                    "http://127.0.0.1:8000/upload_resume/",
                    files={"file": resume_file},
                    data={"overwrite": "true"}
                ).json()
                st.success("Resume overwritten successfully!")
                st.json(resp)
        else:
            st.success("Resume uploaded successfully!")
            st.json(resp)
