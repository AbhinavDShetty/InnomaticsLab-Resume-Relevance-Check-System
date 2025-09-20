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

st.set_page_config(page_title="Resume Relevance Check System", layout="wide")
st.title("Automated Resume Relevance Check System")

# ------------------------------
#           USERS
# ------------------------------
USERS = {
    "student1": {"password": "student123", "role": "Student"},
    "student2": {"password": "student123", "role": "Student"},
    "placement1": {"password": "placement123", "role": "Placement Team"},
}

# ------------------------------
#           LOGIN
# ------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = USERS.get(username)
        if user and user['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['role'] = user['role']
            st.session_state['username'] = username
            st.success(f"Logged in as {user['role']} ({username})")
        else:
            st.error("Invalid username or password")


# ------------------------------
# DASHBOARDS
# ------------------------------
def student_dashboard(username):
    st.subheader("👨‍🎓 Student Dashboard")
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    if "overwrite_prompt" not in st.session_state:
        st.session_state["overwrite_prompt"] = False
    if "pending_resume_file" not in st.session_state:
        st.session_state["pending_resume_file"] = None

    if st.button("Upload Resume"):
        if resume_file is None:
            st.warning("Please select a file to upload.")
        else:
            st.session_state["pending_resume_file"] = resume_file
            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/upload_resume/",
                    files={"file": resume_file},
                    data={"username": username, "overwrite": False}
                )
                resp_json = resp.json()
                if "warning" in resp_json:
                    st.warning(resp_json["warning"])
                    st.info("Click below to confirm overwrite.")
                    st.session_state["overwrite_prompt"] = True
                elif "error" in resp_json:
                    st.error(resp_json["error"])
                else:
                    st.success("Resume uploaded successfully!")
                    st.json(resp_json)
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state["overwrite_prompt"]:
        if st.button("Overwrite existing resume?"):
            try:
                resume_file = st.session_state["pending_resume_file"]
                resume_file.seek(0)
                overwrite_resp = requests.post(
                    "http://127.0.0.1:8000/upload_resume/",
                    files={"file": resume_file},
                    data={"username": username, "overwrite": True}
                )
                overwrite_json = overwrite_resp.json()
                st.success("Resume overwritten successfully!")
                st.json(overwrite_json)
                st.session_state["overwrite_prompt"] = False
            except Exception as e:
                st.error(f"Error overwriting: {e}")


def placement_dashboard():
    st.subheader("🧑‍💼 Placement Team Dashboard")
    jd_file = st.file_uploader("Upload JD (PDF/DOCX)", type=["pdf", "docx"])
    if st.button("Upload JD"):
        if jd_file is None:
            st.warning("Please select a JD file to upload.")
        else:
            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/upload_jd/",
                    files={"file": jd_file}
                )
                resp_json = resp.json()
                if "error" in resp_json:
                    st.error(resp_json["error"])
                else:
                    st.success("JD uploaded successfully!")
                    st.json(resp_json)
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")

    st.markdown("---")
    st.subheader("📄 Uploaded Resumes")

    # Initialize toggle state
    if "show_resumes" not in st.session_state:
        st.session_state["show_resumes"] = False

    # Toggle function
    def toggle_resumes():
        st.session_state["show_resumes"] = not st.session_state["show_resumes"]

    # Dynamic button
    st.button(
        "Show All Resumes" if not st.session_state["show_resumes"] else "Hide Resumes",
        on_click=toggle_resumes
    )

    # Show resumes only if toggled ON
    if st.session_state["show_resumes"]:
        try:
            resp = requests.get("http://127.0.0.1:8000/resumes/")
            if resp.status_code == 200:
                resumes = resp.json()
                if len(resumes) == 0:
                    st.info("No resumes uploaded yet.")
                else:
                    for r in resumes:
                        with st.expander(f"📄 {r['candidate_name']} (Student: {r.get('username', 'N/A')})"):
                            st.write(f"**Preview:** {r['preview']}")
            else:
                st.error(f"Failed to fetch resumes. Status code: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend: {e}")


# ------------------------------
# MAIN ROUTER
# ------------------------------
if st.session_state.get('logged_in'):
    role = st.session_state['role']
    username = st.session_state['username']

    st.sidebar.success(f"Logged in as {role} ({username})")

    # 🚪 Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    # Direct switch to correct dashboard
    if role == "Student":
        student_dashboard(username)
    elif role == "Placement Team":
        placement_dashboard()




#working ----------------------------------------------------------------------------

# import streamlit as st
# import requests

# st.set_page_config(page_title="Resume Relevance Check System", layout="wide")
# st.title("Automated Resume Relevance Check System")

# # ------------------------------
# #           USERS
# # ------------------------------
# USERS = {
#     "student1": {"password": "student123", "role": "Student"},
#     "student2": {"password": "student123", "role": "Student"},
#     "placement1": {"password": "placement123", "role": "Placement Team"},
# }

# # ------------------------------
# #           LOGIN
# # ------------------------------
# if 'logged_in' not in st.session_state:
#     st.session_state['logged_in'] = False

# if not st.session_state['logged_in']:
#     st.subheader("🔑 Login")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         user = USERS.get(username)
#         if user and user['password'] == password:
#             st.session_state['logged_in'] = True
#             st.session_state['role'] = user['role']
#             st.session_state['username'] = username
#             st.success(f"Logged in as {user['role']} ({username})")
#         else:
#             st.error("Invalid username or password")

# # ------------------------------
# #           DASHBOARD
# # ------------------------------
# if st.session_state.get('logged_in'):
#     role = st.session_state['role']
#     username = st.session_state['username']
#     st.write(f"Logged in as **{role}** ({username})")

#     # --------------------------
#     #   STUDENT DASHBOARD
#     # --------------------------
#     if role == "Student":
#         st.subheader("👨‍🎓 Student Dashboard")
#         resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
#         if "overwrite_prompt" not in st.session_state:
#             st.session_state["overwrite_prompt"] = False
#         if "pending_resume_file" not in st.session_state:
#             st.session_state["pending_resume_file"] = None

#         # Upload attempt
#         if st.button("Upload Resume"):
#             if resume_file is None:
#                 st.warning("Please select a file to upload.")
#             else:
#                 st.session_state["pending_resume_file"] = resume_file
#                 try:
#                     resp = requests.post(
#                         "http://127.0.0.1:8000/upload_resume/",
#                         files={"file": resume_file},
#                         data={"username": username, "overwrite": False}
#                     )
#                     resp_json = resp.json()
#                     if "warning" in resp_json:
#                         st.warning(resp_json["warning"])
#                         st.info("Click below to confirm overwrite.")
#                         st.session_state["overwrite_prompt"] = True
#                     elif "error" in resp_json:
#                         st.error(resp_json["error"])
#                     else:
#                         st.success("Resume uploaded successfully!")
#                         st.json(resp_json)
#                 except Exception as e:
#                     st.error(f"Error: {e}")

#         # Handle overwrite separately
#         if st.session_state["overwrite_prompt"]:
#             if st.button("Overwrite existing resume?"):
#                 try:
#                     resume_file = st.session_state["pending_resume_file"]
#                     resume_file.seek(0)
#                     overwrite_resp = requests.post(
#                         "http://127.0.0.1:8000/upload_resume/",
#                         files={"file": resume_file},
#                         data={"username": username, "overwrite": True}
#                     )
#                     overwrite_json = overwrite_resp.json()
#                     st.success("Resume overwritten successfully!")
#                     st.json(overwrite_json)
#                     # Reset prompt
#                     st.session_state["overwrite_prompt"] = False
#                 except Exception as e:
#                     st.error(f"Error overwriting: {e}")

#     # --------------------------
#     # PLACEMENT DASHBOARD
#     # --------------------------
#     elif role == "Placement Team":
#         st.subheader("🧑‍💼 Placement Team Dashboard")
#         jd_file = st.file_uploader("Upload JD (PDF/DOCX)", type=["pdf", "docx"])
#         if st.button("Upload JD"):
#             if jd_file is None:
#                 st.warning("Please select a JD file to upload.")
#             else:
#                 try:
#                     resp = requests.post(
#                         "http://127.0.0.1:8000/upload_jd/",
#                         files={"file": jd_file}
#                     )
#                     try:
#                         resp_json = resp.json()
#                     except:
#                         st.error("Server returned invalid JSON:")
#                         st.text(resp.text)
#                     else:
#                         if "error" in resp_json:
#                             st.error(resp_json["error"])
#                         else:
#                             st.success("JD uploaded successfully!")
#                             st.json(resp_json)
#                 except requests.exceptions.RequestException as e:
#                     st.error(f"Error connecting to backend: {e}")

#         st.markdown("---")
#         st.subheader("📄 Uploaded Resumes")
#         if st.button("Show All Resumes"):
#             try:
#                 resp = requests.get("http://127.0.0.1:8000/resumes/")
#                 if resp.status_code == 200:
#                     try:
#                         resumes = resp.json()
#                     except:
#                         st.error("Server returned invalid JSON for resumes:")
#                         st.text(resp.text)
#                     else:
#                         if len(resumes) == 0:
#                             st.info("No resumes uploaded yet.")
#                         else:
#                             for r in resumes:
#                                 st.write(f"**{r['candidate_name']}** (Student: {r.get('username', 'N/A')})")
#                                 st.write(f"Preview: {r['preview']}")
#                                 st.markdown("---")
#                 else:
#                     st.error(f"Failed to fetch resumes. Status code: {resp.status_code}")
#             except requests.exceptions.RequestException as e:
#                 st.error(f"Error connecting to backend: {e}")
