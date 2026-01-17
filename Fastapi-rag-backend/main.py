from fastapi import FastAPI
from app.api.document import router as document_router # Import your router
from app.db.sql import engine
from app.db.model import Base,Document

# 1. Create the Database Tables (Run this once)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG API")

# 2. CONNECT THE ROUTER
# This tells FastAPI: "All routes in document_router now start with /documents"
app.include_router(document_router)

@app.get("/")
def root():
    return {"message": "RAG System is Online"}