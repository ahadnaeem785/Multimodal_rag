import streamlit as st
import requests
from pathlib import Path
import base64
import fitz 

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Multimodal RAG Assistant", layout="wide")

# --- Chat styling ---
st.markdown("""
    <style>
        .chat-container {
            max-height: 75vh;
            overflow-y: auto;
            padding: 1em;
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 10px;
            margin-bottom: 1em;
        }
        .chat-entry {
            margin-bottom: 1em;
        }
        .user-msg {
            color: #00cfff;
            font-weight: bold;
        }
        .assistant-msg {
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload Files", "Ask Questions", "PDF Viewer", "Video Player", "Status"])

# --- State management ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Upload Page --- #
if page == "Upload Files":
    st.header("📤 Upload PDFs or MP4s")
    uploaded_file = st.file_uploader("Choose a PDF or MP4 file", type=["pdf", "mp4"])

    if uploaded_file is not None:
        if st.button("Upload and Process"):
            with st.spinner("Uploading and processing file..."):
                response = requests.post(
                    f"{API_URL}/upload/",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue())}
                )
                if response.status_code == 200:
                    st.success(response.json()["status"])
                else:
                    st.error("Upload failed.")

# --- Ask Question Page --- #
elif page == "Ask Questions":
    st.header("🤖 Ask a Question")
    for item in st.session_state.chat_history:  # CHRONOLOGICAL
        st.markdown(f"<div class='chat-entry user-msg'>🙋‍♂️ You: {item['question']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-entry assistant-msg'>🤖 Assistant: {item['answer']}</div>", unsafe_allow_html=True)
        if item["citations"]:
            st.markdown(
                "<div style='margin-top: -0.5em; font-size: 0.9em; color: #c0c0c0;'>📌 Citations: " +
                ", ".join(item["citations"]) + "</div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Type your question and press Enter"):
        with st.spinner("Getting answer..."):
            response = requests.post(f"{API_URL}/query/", data={"question": prompt})
            if response.status_code == 200:
                data = response.json()
                st.session_state.chat_history.append({
                    "question": prompt,
                    "answer": data["answer"],
                    "citations": data["citations"]
                })
                st.rerun()
            else:
                st.error(response.json().get("error", "Something went wrong."))

# --- PDF Viewer Page --- #
elif page == "PDF Viewer":
    st.header("📄 PDF Viewer with Highlights")
    pdf_file = st.file_uploader("Upload PDF for viewing", type="pdf")
    if pdf_file:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        page_count = len(doc)
        page_num = st.slider("Select page", 1, page_count, 1)
        page = doc.load_page(page_num - 1)
        text = page.get_text()
        highlight_input = st.text_input("Text to highlight (comma-separated phrases)")
        if highlight_input:
            for phrase in highlight_input.split(","):
                phrase = phrase.strip()
                if phrase in text:
                    text = text.replace(phrase, f"<mark>{phrase}</mark>")
        st.markdown(f"<h4>Page {page_num}</h4>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:16px'>{text}</div>", unsafe_allow_html=True)

# --- Video Transcript Viewer --- #
elif page == "Video Player":
    st.header("🎬 Video with Transcript")
    filename = st.text_input("Enter uploaded video filename (e.g. sample.mp4)")
    if filename:
        video_path = Path("uploads") / filename
        transcript_path = Path("uploads") / f"{filename}.transcript.json"

        if video_path.exists():
            st.video(str(video_path))
        else:
            st.error("Video file not found.")

        try:
            transcript = requests.get(f"{API_URL}/transcript/", params={"filename": filename})
            if transcript.status_code == 200:
                transcript_data = transcript.json()
                st.markdown("### Transcript with Timestamps")
                for item in transcript_data:
                    ts = int(item['start'])
                    m, s = divmod(ts, 60)
                    timestamp = f"{m:02}:{s:02}"
                    st.markdown(f"<b>[{timestamp}]</b> {item['text']}", unsafe_allow_html=True)
            else:
                st.warning("Transcript not available.")
        except Exception as e:
            st.error(f"Failed to load transcript: {e}")

# --- Status Page --- #
elif page == "Status":
    st.header("⚙️ System Status")
    with st.spinner("Checking vectorstore status..."):
        try:
            status_resp = requests.get(f"{API_URL}/status/")
            if status_resp.status_code == 200:
                st.success(status_resp.json()["status"])
            else:
                st.error("Unable to fetch status.")
        except Exception as e:
            st.error("Backend unreachable. Ensure FastAPI server is running.")
