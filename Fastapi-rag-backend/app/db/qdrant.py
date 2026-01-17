from qdrant_client import models,QdrantClient
from app.services.embeddings import emddeding
import uuid

import asyncio
from app.services.chunking import chunk_text_service

client = QdrantClient("http://localhost:6333")



def sync_to_qdrant(filename: str, chunks: list, vector):
    vector_size = len(vector[0])
    if not client.collection_exists("RAG"):
        client.create_collection(
            collection_name="RAG",
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )

    # 2. Prepare Points
    points = []
    # Generate vectors (using your embedding model)
    

    for idx, (chunk_text, vec) in enumerate(zip(chunks, vector)):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec.tolist() if hasattr(vec, "tolist") else vec,
                payload={
                    "text": chunk_text,
                    "filename": filename,
                    "chunk_id": idx
                }
            )
        )

    # 3. Upload
    client.upload_points(collection_name="RAG", points=points)
    return