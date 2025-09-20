# import streamlit as st
# import requests

# st.title("📄 Automated Resume Relevance Check System")

# # Upload JD
# jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])

# # Upload Resume
# resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# if st.button("Upload Files"):
#     if jd_file:
#         resp = requests.post("http://127.0.0.1:8000/upload_jd/", files={"file": jd_file})
#         st.write("JD Upload:", resp.json())

#     if resume_file:
#         resp = requests.post("http://127.0.0.1:8000/upload_resume/", files={"file": resume_file})
#         st.write("Resume Upload:", resp.json())
import streamlit as st
import requests

st.title("📄 Automated Resume Relevance Check System")

# Login form
if 'logged_in' not in st.session_state:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        USERS = {
            "student1": {"password": "student123", "role": "Student"},
            "placement1": {"password": "placement123", "role": "Placement Team"},
        }
        user = USERS.get(username)
        if user and user['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['role'] = user['role']
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")

# Show dashboard based on role
if st.session_state.get('logged_in'):
    role = st.session_state['role']
    st.write(f"Logged in as {role} ({st.session_state['username']})")

    if role == "Student":
        st.subheader("👨‍🎓 Student Dashboard")
        resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        if st.button("Upload Resume"):
            if resume_file:
                resp = requests.post("http://127.0.0.1:8000/upload_resume/", files={"file": resume_file})
                st.write(resp.json())

    elif role == "Placement Team":
        st.subheader("🧑‍💼 Placement Team Dashboard")
        jd_file = st.file_uploader("Upload JD (PDF/DOCX)", type=["pdf", "docx"])
        if st.button("Upload JD"):
            if jd_file:
                resp = requests.post("http://127.0.0.1:8000/upload_jd/", files={"file": jd_file})
                st.write(resp.json())

        if st.button("Show Uploaded Resumes"):
            resp = requests.get("http://127.0.0.1:8000/resumes/")
            if resp.status_code == 200:
                for r in resp.json():
                    st.write(f"**{r['candidate_name']}**")
                    st.write(f"Preview: {r['preview']}")
                    st.markdown("---")
