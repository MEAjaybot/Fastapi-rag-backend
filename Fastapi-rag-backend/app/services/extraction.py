from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Literal
import os
import uuid
import pdfplumber
from io import BytesIO



UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def extract_text(file: UploadFile)-> dict:
    filename = file.filename.lower()
    if not filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed.")
    
    content = await file.read()
    extracted_text = ""
    document_id = str(uuid.uuid4())

    if filename.endswith((".pdf")):
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    extracted_text += t + "\n"

    else:
        extracted_text = content.decode("utf-8", errors="ignore")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="The uploaded file is empty or has no readable text.")
    
    
    


    return {
        "filename": file.filename,
        "char_count": len(extracted_text),
        "preview": extracted_text
    }
