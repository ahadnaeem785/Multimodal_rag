import hashlib
import os
import pdfplumber
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from moviepy import VideoFileClip


def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def process_pdf(file_path, file_hash):
    docs, metadatas = [], []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_text(text)
            for chunk in chunks:
                metadata = {"type": "pdf", "page": i + 1, "source": file_path, "hash": file_hash}
                chunk_with_meta = f"[Page {metadata['page']}] {chunk}"
                docs.append(chunk_with_meta)
                metadatas.append(metadata)
    return docs, metadatas


def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = tempfile.mktemp(suffix=".wav")
    video.audio.write_audiofile(audio_path)
    return audio_path
