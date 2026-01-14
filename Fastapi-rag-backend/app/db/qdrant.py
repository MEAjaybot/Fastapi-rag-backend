from qdrant_client import models,QdrantClient
import uuid
from app.services.embeddings import emddeding
from app.api.document import upload_document
import asyncio
from app.services.chunking import chunk_text_service

client = QdrantClient(":memory:")
async def main_pipeline(file):

    data = await upload_document(file)
    return  data["filename"],data["preview"]

filename,text = main_pipeline()
chunks = chunk_text_service(text, strategy="recursive")  

embedding = emddeding()


client.create_collection(
    collection_name="RAG",
    vectors_config=models.VectorParams(size=embedding.get_sentence_embedding_dimension(),  
        distance=models.Distance.COSINE)
)

points=[]
for idx,(chunk_text,vector) in enumerate(zip(chunks,embedding)):
    points.append(
        models.PointStruct(id=str(uuid.uuid4()),
        vector = embedding,
        payload = {
            "text":chunk_text,
            "filename":filename,
            "chunk_id": idx}
        )
    )

client.upload_points(collection_name="RAG", points=points)


