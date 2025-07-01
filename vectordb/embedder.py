from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embedded_text(text:str):
    return model.encode(text).tolist()