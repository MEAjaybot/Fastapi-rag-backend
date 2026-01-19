from fastapi import FastAPI
from app.api.document import router as document_router # Import your router
from app.db.sql import engine
from app.db.model import Base,Document
from app.api.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

# 1. Create the Database Tables (Run this once)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Swagger, Frontend, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],
)

# 2. CONNECT THE ROUTER
# This tells FastAPI: "All routes in document_router now start with /documents"
app.include_router(document_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "RAG System is Online"}