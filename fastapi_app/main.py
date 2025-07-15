from fastapi import FastAPI, Form, UploadFile, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from auth_clerk import get_current_user_id, get_current_user
import jwt
import requests

import os, sys, subprocess, uuid, tempfile, shutil
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from dotenv import load_dotenv
import pathlib

root_env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=root_env_path)

app = FastAPI(title="CrawlMind FastAPI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "http://localhost:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("DATABASE_PATH", "./crawlmind_db")

@app.get("/")
def read_root():
    return {"status": "✅ CrawlMind FastAPI is running!", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database_path": DB_PATH}

@app.get("/verify-token")
def verify_token(user: dict = Depends(get_current_user)):
    # Extract all useful user information from the token
    user_id = user.get("user_id") or user.get("sub") or user.get("id")
    
    # Get name from various possible fields
    name = None
    if user.get("name"):
        name = user.get("name")
    elif user.get("firstName") and user.get("lastName"):
        name = f"{user.get('firstName')} {user.get('lastName')}"
    elif user.get("given_name") and user.get("family_name"):
        name = f"{user.get('given_name')} {user.get('family_name')}"
    else:
        # Fallback to user ID
        name = f"User {user_id[:8]}"
    
    # Get profile image
    profile_image = None
    for img_field in ['image_url', 'picture', 'profile_image_url', 'avatar_url', 'image']:
        if img_field in user and user.get(img_field):
            profile_image = user.get(img_field)
            break
    
    # Return comprehensive user data
    return {
        "status": "valid",
        "user_id": user_id,
        "name": name,
        "profile_image": profile_image,
        "token_valid": True,
        "all_fields": user  # Include all fields for debugging
    }

@app.post("/verify-token")
async def verify_token_post(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "No Authorization header found", "status": "missing_auth"}
        
        if not auth_header.startswith("Bearer "):
            return {"error": "Authorization header doesn't start with 'Bearer '", "status": "invalid_format"}
        
        token = auth_header.split(" ")[1]
        
        
        try:
            from auth_clerk import verify_clerk_token
            payload = verify_clerk_token(token)
            return {
                "status": "valid",
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "token_valid": True,
                "payload": payload
            }
        except Exception as e:
            
            try:
                import json
                
                
                header = jwt.get_unverified_header(token)
                payload = jwt.decode(token, options={"verify_signature": False})
                
                try:
                    from auth_clerk import get_jwks
                    jwks = get_jwks()
                    jwks_status = f"✅ JWKS fetched successfully ({len(jwks.get('keys', []))} keys)"
                    available_kids = [k.get('kid') for k in jwks.get('keys', [])]
                except Exception as jwks_error:
                    jwks_status = f"❌ JWKS fetch failed: {jwks_error}"
                    available_kids = []
                
                return {
                    "status": "invalid",
                    "error": str(e),
                    "debug_info": {
                        "token_length": len(token),
                        "header": header,
                        "payload": payload,
                        "jwks_status": jwks_status,
                        "available_kids": available_kids,
                        "token_kid": header.get('kid'),
                        "kid_match": header.get('kid') in available_kids,
                        "issuer": payload.get("iss"),
                        "audience": payload.get("aud"),
                        "subject": payload.get("sub"),
                        "expiration": payload.get("exp"),
                        "issued_at": payload.get("iat")
                    }
                }
            except Exception as debug_error:
                return {"status": "error", "error": str(e), "debug_error": str(debug_error)}
    except Exception as e:
        return {"status": "error", "error": f"Request processing error: {e}"}

@app.post("/debug-token")
async def debug_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=400,
            content={"error": "Missing or invalid Authorization header"}
        )
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        from auth_clerk import CLERK_JWKS_URL
        jwks_response = requests.get(CLERK_JWKS_URL, timeout=10)
        jwks_status = jwks_response.status_code
        
        return {
            "status": "debug_only",
            "message": "This is only for debugging, not for production use",
            "token_length": len(token),
            "token_parts": len(token.split(".")),
            "decoded_header": jwt.get_unverified_header(token),
            "decoded_payload": decoded,
            "claims_present": list(decoded.keys()),
            "jwks_endpoint": CLERK_JWKS_URL,
            "jwks_status": jwks_status,
            "custom_user_id": decoded.get("user_id"),
            "sub": decoded.get("sub"),
            "email": decoded.get("email")
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Token debug failed: {str(e)}"}
        )

def safe_clear_database(user_id: str):
    user_db_path = f"{DB_PATH}/{user_id}"
    if os.path.exists(user_db_path):
        try:
            import gc
            import time
            gc.collect()
            
            for attempt in range(3):
                try:
                    shutil.rmtree(user_db_path)
                    return {"success": True, "message": "Database cleared"}
                except PermissionError:
                    if attempt < 2:
                        time.sleep(1)
                        gc.collect()
                    else:
                        
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_path = f"{user_db_path}_{timestamp}"
                        return {"success": True, "message": f"Using new database: {new_path}", "new_path": new_path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database cleanup error: {str(e)}")
    return {"success": True, "message": "No existing database to clear"}

@app.post("/embed")
async def embed_docs(
    request: Request,
    urls: list[str] = Form(None),
    gemini_api_key: str = Form(...),
    files: list[UploadFile] = None,
    user_id: str = Depends(get_current_user_id)
):
    try:
        # Use consistent database path with timestamped collection names
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        user_db_path = f"{DB_PATH}/{user_id}"  # User-specific folder within main DB path
        collection_name = f"{user_id}_collection_{timestamp}"
        
        print(f"Using database: {user_db_path} with collection: {collection_name}")
        
        # Using the GitHub repo style ChromaDB initialization - no Settings object
        chroma_client = PersistentClient(path=user_db_path)
        collection = chroma_client.get_or_create_collection(name=collection_name)

        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )

        all_chunks = []

       
        if urls:
            for url in urls:
                try:
                    # Get the project root directory (one level up from fastapi_app)
                    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                    crawler_path = os.path.join(project_root, "crawler.py")
                    
                    # Run crawler with the correct path and capture output
                    print(f"Crawling URL: {url}")
                    result = subprocess.run(
                        [sys.executable, crawler_path, url], 
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    # Log crawler output for debugging
                    if result.returncode != 0:
                        print(f"Warning: Crawler exited with non-zero code: {result.returncode}")
                    
                    if result.stdout:
                        print(f"Crawler stdout: {result.stdout[:200]}...")
                    if result.stderr:
                        print(f"Crawler stderr: {result.stderr}")
                    
                    # Use the absolute path to the crawled content file
                    crawled_file = os.path.join(project_root, "crawled_content.md")
                    
                    if os.path.exists(crawled_file):
                        with open(crawled_file, "r", encoding="utf-8") as f:
                            text = f.read().strip()
                            if text and not text.startswith("# Failed to crawl") and not text.startswith("# Error crawling"):
                                all_chunks.append(text)
                                print(f"✅ Successfully added content from {url} ({len(text)} characters)")
                            else:
                                print(f"⚠️ Failed to extract valid content from {url}")
                    else:
                        print(f"❌ Error: Crawled content file not found at: {crawled_file}")
                except Exception as e:
                    print(f"❌ Error crawling {url}: {str(e)}")

        
        if files:
            for file in files:
                try:
                    suffix = file.filename.split(".")[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp_file:
                        tmp_file.write(await file.read())
                        tmp_path = tmp_file.name

                    loader = PyPDFLoader(tmp_path) if suffix == "pdf" else TextLoader(tmp_path)
                    docs = loader.load()
                    for doc in docs:
                        if doc.page_content.strip():
                            all_chunks.append(doc.page_content.strip())
                    
                    os.unlink(tmp_path)  
                except Exception as e:
                    print(f"Error processing file {file.filename}: {str(e)}")

        embeddings, ids, valid_chunks = [], [], []
        try:
            for chunk in all_chunks:
                emb = embedding_function.embed_query(chunk)
                embeddings.append(emb)
                ids.append(str(uuid.uuid4()))
                valid_chunks.append(chunk)
        except Exception as e:
            if "API_KEY_INVALID" in str(e):
                raise HTTPException(status_code=400, detail="Invalid Gemini API key")
            else:
                raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

        if valid_chunks:
            collection.add(documents=valid_chunks, embeddings=embeddings, ids=ids)
            
            return JSONResponse({
                "status": f"✅ Embedded {len(valid_chunks)} chunks for user {user_id}",
                "chunks_added": len(valid_chunks),
                "database_path": user_db_path,
                "success": True
            })
        else:
            if all_chunks:
                message = "Failed to create embeddings for the content"
                print(f"⚠️ {message}")
                return JSONResponse({
                    "status": f"⚠️ {message}",
                    "chunks_added": 0,
                    "success": False,
                    "error": "No embeddings created despite having content"
                }, status_code=422)
            else:
                message = "No valid content found to embed"
                print(f"⚠️ {message}")
                return JSONResponse({
                    "status": f"⚠️ {message}",
                    "chunks_added": 0,
                    "success": False,
                    "error": "No content extracted from URLs or files"
                }, status_code=422)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/query")
async def query_docs(
    request: Request,
    question: str = Form(...),
    gemini_api_key: str = Form(...),
    user_id: str = Depends(get_current_user_id)
):
    try:

        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )

    
        user_db_path = f"{DB_PATH}/{user_id}"
        if not os.path.exists(user_db_path):
            raise HTTPException(status_code=404, detail="No documents found. Please upload documents first.")
            
        # Find the most recent collection for this user
        try:
            chroma_client = PersistentClient(path=user_db_path)
            collections = chroma_client.list_collections()
            
            # Filter collections that belong to this user and sort by timestamp
            user_collections = [c for c in collections if c.name.startswith(f"{user_id}_collection_")]
            
            if not user_collections:
                raise HTTPException(status_code=404, detail="No documents found. Please upload documents first.")
                
            # Get the most recent collection (assuming the timestamp format sorts correctly)
            latest_collection = sorted(user_collections, key=lambda c: c.name, reverse=True)[0]
            collection_name = latest_collection.name
            
            print(f"Using most recent collection: {collection_name}")
            
            # Using the GitHub repo style ChromaDB initialization for the query
            db = Chroma(
                client=PersistentClient(path=user_db_path),
                collection_name=collection_name,
                embedding_function=embedding_function
            )
        except Exception as e:
            print(f"Error finding collection: {e}")
            raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

        retriever = db.as_retriever()
        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs]) or "No relevant context found."

        llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.3
        )

        rag_prompt = PromptTemplate.from_template("""
        You are CrawlMind AI assistant for question-answering tasks.
        Use the retrieved context below to answer the question.
        If you don't know the answer based on the context, say you don't know.
        If the user says bye or goodbye, respond appropriately and end the conversation.

        Context:
        {context}

        Question:
        {question}

        Answer in 2-3 clear sentences.
        """)

        answer = llm.invoke(rag_prompt.format(context=context, question=question))

        return JSONResponse({
            "answer": answer,
            "context_used": context[:500] + "..." if len(context) > 500 else context,
            "sources_count": len(docs)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.get("/debug/jwks")
def debug_jwks():
    try:
        from auth_clerk import get_jwks
        jwks = get_jwks()
        return {
            "status": "success",
            "jwks_keys_count": len(jwks.get('keys', [])),
            "jwks": jwks
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "jwks": None
        }

@app.get("/debug/routes")
def debug_routes():
    return {
        "routes": [
            {
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else [],
                "name": getattr(route, 'name', None)
            }
            for route in app.routes
        ]
    }

@app.get("/test-debug")
def test_debug():
    return {"message": "Debug endpoint is working"}

@app.get("/debug-token")
def debug_token(user: dict = Depends(get_current_user)):
    """Debug endpoint to inspect all token claims"""
    import json
    
    # Extract all available claims
    user_id = user.get("user_id") or user.get("sub") or user.get("id")
    
    # Get name from various possible fields
    name = None
    if user.get("name"):
        name = user.get("name")
    elif user.get("firstName") and user.get("lastName"):
        name = f"{user.get('firstName')} {user.get('lastName')}"
    else:
        name = "User"
    
    # Construct a summary of the token
    token_summary = {
        "user_id": user_id,
        "name": name,
        "all_claims": list(user.keys()),
        "full_token": user  # Include the entire token for debugging
    }
    
    return token_summary
