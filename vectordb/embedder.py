
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

def embedded_chunks(chunks: list[str]):
    embeddings = model.encode(chunks)
    return [emb.tolist() for emb in embeddings]

