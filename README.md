# Fastapi-rag-backend
This project implements a backend system for document ingestion and
retrieval-augmented generation (RAG) using FastAPI.

It supports uploading PDF/TXT documents, semantic search using vector
databases, multi-turn conversational queries, and interview booking
through a stateful chat interface.

## Features
- Document ingestion API for PDF/TXT files
- Selectable chunking strategies
- Vector search using Qdrant
- Custom RAG pipeline (no RetrievalQAChain)
- Multi-turn chat using Redis memory
- Interview booking with structured storage

## Tech Stack
- FastAPI – REST API framework
- Qdrant – Vector database
- Redis – Chat memory
- PostgreSQL – Interview booking storage
- LLM – Local or API-based(0llama)

## System Architecture
PDF/TXT Upload → Chunking → Embeddings → Qdrant → PostgreSQL(document metadata)  
Chat Query → Vector Search → Context Injection → LLM  
Redis → Conversation Memory  
PostgreSQL → Interview Booking

## API Endpoints

### Document Ingestion
POST /documents/upload

### Conversational RAG
POST /chat/ask


## Interview Booking
The system detects booking intent and collects required fields
(Name, Email, Date, Time) across multiple turns before storing the
booking in PostgreSQL.

Due to API quota limitations with Gemini,  
I switched to a local Mistral model using Ollama without changing the RAG pipeline.

The project uses Docker to containerize external services such as
Qdrant, Redis, and PostgreSQL. Docker volumes are configured to ensure


