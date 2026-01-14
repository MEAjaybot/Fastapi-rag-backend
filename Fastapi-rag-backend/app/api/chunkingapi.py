# routers/chunking.py
from fastapi import APIRouter, Form
from typing import Literal
from services.chunking import chunk_text_service

router = APIRouter(prefix="/chunking", tags=["Chunking"])

@router.post("/")
async def chunk_text_api(
    text: str = Form(...),
    chunk_strategy: Literal["fixed", "recursive"] = "fixed"
):
    chunks = chunk_text_service(text, chunk_strategy)

    return {
        "strategy": chunk_strategy,
        "original_char_count": len(text),
        "num_chunks": len(chunks),
        "chunks": chunks
    }
