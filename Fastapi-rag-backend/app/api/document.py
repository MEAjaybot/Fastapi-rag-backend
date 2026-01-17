from fastapi import APIRouter, UploadFile, File,Depends
from app.services.extraction import extract_text
import uuid
from sqlalchemy.orm import Session
from app.db.sql import SessionLocal
from app.db.model import Document
from app.services.chunking import chunk_text_service
from typing import Literal
from app.db.qdrant import sync_to_qdrant
from app.services.embeddings import emddeding


router = APIRouter(prefix="/documents", tags=["Documents"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DOCUMENT_STORE = {}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...),chunk_strategy: Literal["fixed", "recursive"] = "fixed",
                          db: Session = Depends(get_db)):
    doc = await extract_text(file)

    document_id = str(uuid.uuid4())
    DOCUMENT_STORE[document_id] = doc
    

    chunks = chunk_text_service(doc["preview"], chunk_strategy)
    
    new_doc = Document(
        filename=doc["filename"],
        file_type=file.content_type,
        chunk_strategy = chunk_strategy,
        num_chunks = len(chunks)
        )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    vectors = emddeding(chunks)
    sync_to_qdrant(doc["filename"], chunks, vectors)


    return {
        "document_id": document_id,
        "filename": file.content_type,
        "strategy": chunk_strategy,
        "num_chunks": len(chunks),
        "status": "Complete",
        "qdrant": "Check dashboard",
    }
