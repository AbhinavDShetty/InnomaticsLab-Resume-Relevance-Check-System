import streamlit as st
import requests

st.set_page_config(page_title="Placement Dashboard", layout="wide")
st.title("🧑‍💼 Placement Team Dashboard")

# Role check
if st.session_state.get('role') != 'Placement Team':
    st.warning("You must log in as Placement Team!")
    st.stop()

st.write(f"Logged in as: {st.session_state.get('username')}")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
if st.button("Upload JD"):
    if jd_file:
        resp = requests.post(
            "http://127.0.0.1:8000/upload_jd/",
            files={"file": jd_file}
        )
        st.write(resp.json())

# Show Uploaded Resumes
if st.button("Show Uploaded Resumes"):
    resp = requests.get("http://127.0.0.1:8000/resumes/")
    if resp.status_code == 200:
        for r in resp.json():
            st.write(f"**{r['candidate_name']}**")
            st.write(f"Preview: {r['preview']}")
            st.markdown("---")
