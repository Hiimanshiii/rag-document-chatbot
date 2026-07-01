from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File
from app.vectorstore import (
    create_vector_store,
    save_vector_store,
)
from app.loader import load_pdf
from app.rag import chunk_documents
import shutil
from pathlib import Path
from app.chain import ask_question

app = FastAPI(
    title="Chat With Your Docs API",
    description="A Retrieval-Augmented Generation (RAG) API using LangChain and FAISS",
    version="1.0.0"
)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Welcome to Chat With Your Docs!",
        "status": "API is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and save it locally.
    """

    # Validate file type
    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed."
        }

    save_path = UPLOAD_FOLDER / file.filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 👇 Add these lines here
    documents = load_pdf(str(save_path))

    chunks = chunk_documents(documents)

    vectorstore = create_vector_store(chunks)

    save_vector_store(vectorstore)

    answer = ask_question(
        "What skills does this candidate have?"
    )

    # 👇 Then return the response
    return {
        "message": "File uploaded successfully!",
        "filename": file.filename
    }

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: QuestionRequest):

    answer = ask_question(request.question)

    return {
        "question": request.question,
        "answer": answer
    }