# Multimodal RAG Application

An end-to-end Retrieval-Augmented Generation (RAG) system that processes and answers questions based on content from **PDF documents** and **MP4 videos**. It provides rich, context-aware responses with citations such as page numbers and video timestamps.

## 🎥 Demo

https://github.com/user-attachments/assets/93c1e0fc-43f6-47f8-a9ac-9a83dbaa924c



## 🚀 Features

* Upload and process PDF and MP4 files
* Extract text from PDFs and generate transcripts from videos
* Store and retrieve multimodal embeddings using Chroma DB
* Query the data using LLM (Gemini 2.0)
* Citations included in responses (e.g., "Page 3" or "\[00:01 - 00:03]")
* Streamlit frontend with intuitive user interface:

  * File upload
  * Question-answering chat interface
  * PDF viewer with highlights
  * Video player with transcript viewer

---

## 🧠 Tech Stack

| Layer            | Tool/Library              |
| ---------------- | ------------------------- |
| Backend          | FastAPI, Uvicorn          |
| Frontend         | Streamlit                 |
| LLM              | Google Gemini 2.0 Flash   |
| Embeddings       | HuggingFace (nomic-embed) |
| Vector Store     | Chroma DB                 |
| Video Processing | MoviePy + Faster Whisper  |
| PDF Processing   | pdfplumber                |

---

## 🛠 Setup Instructions (with `uv` package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/ahadnaeem785/Multimodal_rag.git
cd Multimodal_rag
```

### 2. Create and Activate Virtual Environment

```bash
uv venv
.venv\Scripts\activate       # For Windows
# OR
source .venv/bin/activate    # For macOS/Linux
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Set Up Environment Variables

Create a `.env` file based on `.env.example` and add your Google API Key:

```env
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_token_here
```

---

## 🧪 Run the Application

Open **two terminals**, and activate the virtual environment in both.

### Terminal 1: Run Backend

```bash
uvicorn backend:app --reload
```

Backend runs at: `http://localhost:8000`

### Terminal 2: Run Frontend (Streamlit)

```bash
uv run streamlit run frontend.py
```

Frontend runs at: `http://localhost:8501`

---

## 🖥 Application Pages

* **Upload Files:** Upload PDF or MP4
* **Ask Questions:** Chat with AI and get citations
* **PDF Viewer:** View and highlight extracted PDF content
* **Video Player:** Watch uploaded video with transcript and timestamps
* **Status:** Check vectorstore readiness

---

## 📁 Folder Structure

```
Multimodal_rag/
├── backend.py             # FastAPI backend
├── frontend.py            # Streamlit frontend
├── chroma_store/          # Vector DB persistence
├── uploads/               # Uploaded files & transcripts
├── llm/                   # (Optional) for LLM logic modules
├── utils/                 # Utility functions
├── .env / .env.example    # Environment configs
├── README.md              # Project instructions
├── pyproject.toml         # Dependency definitions
├── uv.lock                # uv dependency lock
```

---

## 📬 Contact

For issues or queries, reach out via GitHub or open an issue.

---

> **Author:** [Ahad Naeem](https://github.com/ahadnaeem785)
> **Repo:** [github.com/ahadnaeem785/Multimodal\_rag](https://github.com/ahadnaeem785/Multimodal_rag)
