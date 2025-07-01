
from embedder import embedded_chunks
import chromadb

client = chromadb.Client()
collection = client.create_collection(name="crawled_data")

def chrome_db(chunks,vectors):
        
    for chunk, vector in zip(chunks, vectors):
        doc_id = f"chunk_{hash(chunk)}"   

        collection.add(
            documents=[chunk],
            embeddings=[vector],
            ids=[doc_id],
            metadatas=[{"source": "my_crawler", "type": "markdown"}])
    
    print("Stored chunks in ChromaDB!")
