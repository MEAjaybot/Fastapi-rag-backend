from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

def emddeding(chunks: list[str]):
    
    if not chunks:
        return []
    embeddings = model.encode(chunks)
    return embeddings.tolist()