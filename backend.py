from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
import json
from langchain_chroma import Chroma
from llm.embedder import embedding_function
from utils.file_ops import get_file_hash, process_pdf, extract_audio
from utils.transcript_ops import transcribe_audio
from llm.vectorstore import build_vectorstore, vectorstore, retriever, COLLECTION_NAME, PERSIST_DIR
from llm.prompt_template import prompt_template, StructuredAnswer, llm

app = FastAPI()
FILES_DIR = "./uploads"
os.makedirs(FILES_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    msg = build_vectorstore()
    print(f"Startup Vectorstore Load: {msg}")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global vectorstore, retriever 
    content = await file.read()
    filepath = os.path.join(FILES_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(content)
    file_hash = get_file_hash(filepath)

    global vectorstore, retriever
    if vectorstore:
        existing_hashes = {m.get("hash") for m in vectorstore.get()["metadatas"] if m.get("hash")}
        if file_hash in existing_hashes:
            return {"status": "File already exists in vectorstore."}

    pdf_texts, pdf_meta, video_texts, video_meta, transcript = [], [], [], [], []
    if filepath.endswith(".pdf"):
        t, m = process_pdf(filepath, file_hash)
        pdf_texts.extend(t)
        pdf_meta.extend(m)
    elif filepath.endswith(".mp4"):
        audio = extract_audio(filepath)
        t, m, transcript = transcribe_audio(audio, file_hash)
        video_texts.extend(t)
        video_meta.extend(m)

        # Save transcript using clean filename
        clean_name = os.path.splitext(file.filename)[0].replace(" ", "_")
        transcript_path = os.path.join(FILES_DIR, f"{clean_name}.transcript.json")
        with open(transcript_path, "w") as f:
            json.dump(transcript, f)

    all_texts = pdf_texts + video_texts
    all_metas = pdf_meta + video_meta

    if not all_texts:
        return {"status": "No valid content found in file."}

    if vectorstore:
        vectorstore.add_texts(all_texts, metadatas=all_metas)
    else:
        vectorstore = Chroma.from_texts(all_texts, embedding=embedding_function, metadatas=all_metas, persist_directory=PERSIST_DIR, collection_name=COLLECTION_NAME)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    return {"status": "File processed and vectorstore updated."}


@app.get("/status/")
async def status():
    if retriever:
        return {"status": " Vectorstore is ready for queries."}
    else:
        return {"status": " Vectorstore not ready. Please upload files."}


@app.get("/transcript/")
async def get_transcript(filename: str):
    clean_name = filename.replace(".mp4", "").replace(" ", "_")
    path = os.path.join(FILES_DIR, clean_name + ".transcript.json")
    if os.path.exists(path):
        return JSONResponse(content=json.load(open(path)))
    return JSONResponse(content={"error": "Transcript not found."}, status_code=404)


@app.post("/query/")
async def ask_question(question: str = Form(...)):
    if retriever is None:
        return JSONResponse(content={"error": "Vectorstore not initialized."}, status_code=400)

    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    if not context.strip():
        return JSONResponse(content={"error": "No content found to answer the question."}, status_code=400)

    rag_chain = prompt_template | llm.with_structured_output(StructuredAnswer)

    try:
        final_response = rag_chain.invoke({"documents": context, "question": question})
        return final_response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to parse LLM response", "details": str(e)})
