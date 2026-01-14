from fastapi import APIRouter, UploadFile, File
from app.services.extraction import extract_text
import uuid

router = APIRouter(prefix="/documents", tags=["Documents"])

DOCUMENT_STORE = {}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    doc = await extract_text(file)

    document_id = str(uuid.uuid4())
    DOCUMENT_STORE[document_id] = doc

    return {
        "document_id": document_id,
        "filename": doc["filename"]
    }
