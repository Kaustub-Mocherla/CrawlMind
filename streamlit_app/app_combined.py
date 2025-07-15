import os
import sys
import subprocess
import tempfile
import uuid
import shutil
import base64
import pathlib
import time
import gc
import datetime
from dotenv import load_dotenv

root_env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=root_env_path)

import streamlit as st
import requests
import validators
import jwt

# Use simple ChromaDB import without Settings (matching GitHub repo)
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader

st.set_page_config(
    page_title="CrawlMind AI Assistant",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    def load_css(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Try multiple possible paths for the CSS file
    css_paths = ['styles.css', 'streamlit_app/styles.css', os.path.join(os.path.dirname(__file__), 'styles.css')]
    css_loaded = False
    
    for path in css_paths:
        try:
            load_css(path)
            css_loaded = True
            break
        except FileNotFoundError:
            continue
    
    if not css_loaded:
        raise FileNotFoundError("Could not find styles.css in any of the expected locations")
except Exception as e:
    print(f"Error loading CSS: {e}")
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #4A9EFF 0%, #667eea 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .auth-card {
        background: rgba(26, 26, 26, 0.8);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        position: relative;
        overflow: hidden;
    }
    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .upload-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 1rem 0;
    }
    .social-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
    }
    .social-button {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        color: white;
        transition: all 0.3s ease;
    }
    .github {
        background: #24292e;
    }
    .linkedin {
        background: #0077b5;
    }
    .social-button:hover {
        transform: scale(1.1);
    }
    .auth-button {
        background:#4A9EFF;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.85rem 2rem;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        text-decoration: none;
        box-shadow: 0 12px 32px rgba(61, 141, 233, 0.368);
    }
    .auth-button:hover {
        background: #3b82f6;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(74, 158, 255, 0.2);
        text-decoration: none;
    }
    .auth-divider {
        color: rgba(255, 255, 255, 0.5);
        margin: 1.5rem 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    defaults = {
        'authenticated': False,
        'jwt_token': None,
        'user_id': None,
        'user_email': None,
        'user_name': None,
        'user_image': None,
        'gemini_api_key': '',
        'urls': [],
        'uploaded_files': [],
        'chat_history': [],
        'embeddings_created': False,
        'collection': None,
        'logo_base64': None,
        'default_avatar': None,
        'auth_loading': False,
        'debug_mode': False,  # Disable debug mode for production
        'token_payload': None,
        'all_fields': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    if st.session_state.logo_base64 is None:
        try:
            with open("artificial-intelligence.png", "rb") as img_file:
                st.session_state.logo_base64 = base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            st.session_state.logo_base64 = ""

def extract_token_from_url():
    try:
        query_params = st.query_params
        
        if 'token' in query_params:
            token = query_params['token']
            st.session_state.jwt_token = token
            
            if verify_token_with_api(token):
                st.session_state.authenticated = True
                st.query_params.clear()
                return True
        
        if st.session_state.jwt_token:
            return verify_token_with_api(st.session_state.jwt_token)
            
        return False
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

def verify_token_with_api(token: str) -> bool:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # First, try to decode the token locally
        try:
            # Debug mode is disabled for production
            debug_mode = False
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Debug logging disabled in production
                
                # Debug sidebar expander is disabled in production
            
            # Extract user details from token if possible
            for field in ['user_id', 'sub', 'id']:
                if field in decoded and not st.session_state.user_id:
                    st.session_state.user_id = decoded.get(field)
                    break
                    
            # Look for email in various possible fields
            for field in ['email', 'primary_email', 'email_address']:
                if field in decoded and not st.session_state.user_email:
                    st.session_state.user_email = decoded.get(field)
                    break
            
                    # Build user_name safely
            if 'name' in decoded and decoded.get('name'):
                st.session_state.user_name = decoded.get('name')
            elif decoded.get('firstName') and decoded.get('lastName'):
                st.session_state.user_name = f"{decoded.get('firstName')} {decoded.get('lastName')}"
            elif decoded.get('firstName'):
                st.session_state.user_name = decoded.get('firstName')
            elif decoded.get('given_name') and decoded.get('family_name'):
                st.session_state.user_name = f"{decoded.get('given_name')} {decoded.get('family_name')}"
            elif decoded.get('username'):
                st.session_state.user_name = decoded.get('username')
            elif st.session_state.user_email:
                email_name = st.session_state.user_email.split('@')[0]
                st.session_state.user_name = email_name.replace('.', ' ').title()
            else:
                st.session_state.user_name = "User"

            # Look for profile image in various fields
            for field in ['picture', 'image', 'avatar_url', 'profile_image', 'image_url']:
                if field in decoded and not st.session_state.user_image and decoded.get(field):
                    st.session_state.user_image = decoded.get(field)
                    break
            
        except Exception as e:
            # Error handling is silent in production mode
            pass
          # Then verify with backend API
        response = requests.get(
            "http://localhost:8000/verify-token",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            
            # No debug logging in production
            
            # Store user details from API response
            st.session_state.user_id = user_data.get('user_id')
            st.session_state.user_email = user_data.get('email')
            if user_data.get('name'):
                st.session_state.user_name = user_data.get('name')
            elif user_data.get('firstName') and user_data.get('lastName'):
                st.session_state.user_name = f"{user_data.get('firstName')} {user_data.get('lastName')}"
            elif user_data.get('firstName'):
                st.session_state.user_name = user_data.get('firstName')
            elif user_data.get('username'):
                st.session_state.user_name = user_data.get('username')
            elif st.session_state.user_email:
                email_name = st.session_state.user_email.split('@')[0]
                st.session_state.user_name = email_name.replace('.', ' ').title()
            else:
                st.session_state.user_name = "User"


            
            # Get profile image from the response
            if 'profile_image' in user_data and user_data.get('profile_image'):
                st.session_state.user_image = user_data.get('profile_image')
                
            # Store all user data for debugging
            if 'all_fields' in user_data:
                st.session_state.all_fields = user_data.get('all_fields')
                
            # If we still don't have a user name, generate one from email
            if not st.session_state.user_name and st.session_state.user_email:
                email_name = st.session_state.user_email.split('@')[0]
                st.session_state.user_name = email_name.replace('.', ' ').title()
            
            # Generate avatar if we don't have a profile image
            if not st.session_state.user_image and st.session_state.user_name:
                initials = ''.join([name[0].upper() for name in st.session_state.user_name.split()])
                avatar = generate_default_avatar(initials)
                if avatar:
                    st.session_state.user_image = avatar
            
            return True
        else:
            error_msg = f"Token verification failed: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'No details available')
                error_msg += f" - {error_detail}"
            except:
                pass
            st.error(error_msg)
            return False
    except Exception as e:
        st.error(f"Token verification error: {e}")
        return False

def show_auth_required():
    
    st.markdown("""
    <style>
    section.main > div:first-child {
        max-width: 100% !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        
        st.markdown(f'''
        <div style="text-align: center;">
            <div class="auth-header-standalone">
                <img src="data:image/png;base64,{st.session_state.logo_base64}" class="auth-inline-logo" alt="CrawlMind Logo">
                <div class="auth-title-container">
                    <h2 class="auth-title">Welcome to CrawlMind</h2>
                    <p class="auth-subtitle">Professional AI Powered Document Analysis & Intelligence Platform</p>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-card" style="background: rgba(26, 26, 26, 0.8); color: white; padding: 2rem; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-divider" style="color: rgba(255, 255, 255, 0.7); margin: 1rem 0;">Authentication Required</div>', unsafe_allow_html=True)
        
        st.markdown('''
        <a href="http://localhost:3000" class="auth-button" style="color: white; text-decoration: none;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                <polyline points="10 17 15 12 10 7"></polyline>
                <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            <span style="color: white;">Sign in with Clerk</span>
        </a>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-features">', unsafe_allow_html=True)
        st.markdown('''
            <div class="auth-feature-item">
                <div class="auth-feature-icon">✓</div>
                <span>Secure authentication powered by Clerk</span>
            </div>
            <div class="auth-feature-item">
                <div class="auth-feature-icon">✓</div>
                <span>Automatic redirection after login</span>
            </div>
            <div class="auth-feature-item">
                <div class="auth-feature-icon">✓</div>
                <span>Access to all CrawlMind features</span>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="auth-footer">Need help? Check the <a href="https://github.com/Kaustub-Mocherla/CrawlMind" target="_blank">documentation</a></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Manual token entry function removed as tokens are generated elsewhere

def process_documents():
    if not st.session_state.gemini_api_key:
        st.error("❌ Gemini API key required")
        return
    
    if not st.session_state.urls and not st.session_state.uploaded_files:
        st.error("❌ No documents to process")
        return
    
    try:
        # Use consistent database path with timestamped collection names
        db_path = "./crawlmind_db"  # Use the path from .env if available
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        collection_name = f"crawlmind_collection_{timestamp}"
        
        # Initialize ChromaDB with the GitHub repo approach (no Settings)
        with st.spinner("Initializing database..."):
            chroma_client = PersistentClient(path=db_path)
            collection = chroma_client.get_or_create_collection(name=collection_name)

        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=st.session_state.gemini_api_key
        )

        all_chunks = []
        
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        crawler_path = os.path.join(project_root, "crawler.py")
        crawled_content_path = os.path.join(project_root, "crawled_content.md")

        for url in st.session_state.urls:
            # Replace info message with spinner
            try:
                with st.spinner(f"Crawling {url}..."):
                    # Using improved approach with better error handling
                    # Run crawler with timeout and capture output
                    process = subprocess.run(
                        [sys.executable, crawler_path, url],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    # Check for errors in the output or return code
                    if process.returncode != 0:
                        st.error(f"❌ Crawler exited with error code {process.returncode}")
                        st.error(f"Error details: {process.stderr.strip()}")
                        continue
                    
                    # Display crawler output for debugging
                    if st.session_state.get('debug_mode', False):
                        with st.expander("Crawler Output", expanded=False):
                            st.code(process.stdout.strip())
                    
                    # Check if output file exists
                    content_found = False
                    # Look for timestamped files if regular file doesn't exist
                    content_files = [crawled_content_path]
                    if not os.path.exists(crawled_content_path):
                        # Look for alternative timestamped files
                        for f in os.listdir(project_root):
                            if f.startswith("crawled_content.md.") and f.replace("crawled_content.md.", "").isdigit():
                                content_files.append(os.path.join(project_root, f))
                    
                    # Try all potential content files
                    for content_file in content_files:
                        if os.path.exists(content_file):
                            try:
                                with open(content_file, "r", encoding="utf-8") as f:
                                    text = f.read().strip()
                                    if text:
                                        all_chunks.append(text)
                                        st.success(f"✅ Successfully crawled content from {url} ({len(text)} characters)")
                                        content_found = True
                                        break  # Found content, stop looking
                            except Exception as file_error:
                                st.warning(f"⚠️ Error reading {content_file}: {str(file_error)}")
                    
                    # Clean up any timestamped files to avoid confusion in future runs
                    for f in os.listdir(project_root):
                        if f.startswith("crawled_content.md.") and f.replace("crawled_content.md.", "").isdigit():
                            try:
                                os.remove(os.path.join(project_root, f))
                            except:
                                pass  # Ignore cleanup errors
                    
                    if not content_found:
                        st.warning(f"⚠️ No content found in crawled output for {url}")
                        
            except subprocess.TimeoutExpired:
                st.error(f"❌ Crawler timed out after 5 minutes for URL: {url}")
            except Exception as e:
                st.error(f"❌ Error running crawler: {str(e)}")
                import traceback
                if st.session_state.get('debug_mode', False):
                    st.error(traceback.format_exc())

        for file in st.session_state.uploaded_files:
            suffix = file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path) if suffix == "pdf" else TextLoader(tmp_path)
            docs = loader.load()
            for doc in docs:
                if doc.page_content.strip():
                    all_chunks.append(doc.page_content.strip())

        embeddings, ids, valid_chunks = [], [], []
        
        # Use a spinner for the embedding process
        with st.spinner("Processing and embedding content..."):
            try:
                for chunk in all_chunks:
                    emb = embedding_function.embed_query(chunk)
                    embeddings.append(emb)
                    ids.append(str(uuid.uuid4()))
                    valid_chunks.append(chunk)
            except Exception as e:
                if "API_KEY_INVALID" in str(e):
                    st.error("❌ Invalid API key! Please check your Gemini API key.")
                else:
                    st.error(f"❌ Error processing documents: {str(e)}")
                return False

            if valid_chunks:
                collection.add(documents=valid_chunks, embeddings=embeddings, ids=ids)
                st.session_state.collection = collection
                st.session_state.embeddings_created = True
                # Store both the database path and collection name in session state for later use
                st.session_state.db_path = db_path
                st.session_state.collection_name = collection_name
                # Success message is shown outside the spinner
                st.success(f"✅ Successfully embedded {len(valid_chunks)} chunks")
                return True

        # If we get here, there were no valid chunks
        if all_chunks:
            st.error("❌ Failed to create embeddings for the content.")
            st.info("This could be due to API limits or content format issues.")
        else:
            st.warning("⚠️ No valid content found to embed!")
            st.info("Try a different URL or upload a document directly.")
        return False
    
    except Exception as e:
        st.error(f"❌ Error processing documents: {e}")
        return False

def query_documents(question: str) -> str:
    if not st.session_state.embeddings_created and not st.session_state.collection:
        return "❌ Please process some documents first."
    
    if not st.session_state.gemini_api_key:
        return "❌ Gemini API key required."
    
    try:
        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=st.session_state.gemini_api_key
        )

        # Use the database path from the crawl & embed step if available
        db_path = getattr(st.session_state, "db_path", "./crawlmind_db")
        
        try:
            # Use collection name from session state if available, otherwise find the most recent collection
            with st.spinner("Preparing knowledge base..."):
                if hasattr(st.session_state, "collection_name") and st.session_state.collection_name:
                    collection_name = st.session_state.collection_name
                    # Removed notification
                else:
                    # Find the most recent collection
                    chroma_client = PersistentClient(path=db_path)
                    collections = chroma_client.list_collections()
                    
                    # Filter collections that match our naming pattern and sort by timestamp
                    relevant_collections = [c for c in collections if c.name.startswith("crawlmind_collection_")]
                    
                    if not relevant_collections:
                        st.error("❌ No collections found in the database. Please run the 'Crawl & Embed' step first.")
                        return
                        
                    # Get the most recent collection (assuming the timestamp format sorts correctly)
                    latest_collection = sorted(relevant_collections, key=lambda c: c.name, reverse=True)[0]
                    collection_name = latest_collection.name
                    # Removed notification
            
            db = Chroma(
                client=PersistentClient(path=db_path),
                collection_name=collection_name,
                embedding_function=embedding_function
            )
        except Exception as db_error:
            st.error(f"❌ Error connecting to database: {str(db_error)}")
            st.info("If the error persists, try clearing and recreating your database.")
            return
        retriever = db.as_retriever()
        llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=st.session_state.gemini_api_key,
            temperature=0.3
        )

        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs]) or "No relevant context found."

        rag_prompt = PromptTemplate.from_template("""
You are an CrawlMind AI assistant for question-answering tasks.
Use the retrieved context below to answer the question.
If you don't know, say you don't know.
if the user says bye or goodbye somrthing like that, say goodbye and end the conversation.

Context:
{context}
                                              
Question:
{question}

Answer in 2-3 clear sentences.
""")

        final_prompt = rag_prompt.format(
            context=context,
            question=question
        )

        answer = llm.invoke(final_prompt)
        return answer
    
    except Exception as e:
        return f"❌ Error querying documents: {e}"

def show_main_app():
    st.markdown("""
        <div style="text-align: center; margin: 2rem 0; margin-bottom: 4rem;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <img src="data:image/png;base64,{}" style="width: 80px; height: 80px; margin-right: 20px;" alt="CrawlMind Logo">
                <h1 style="font-size: 3.5rem; font-weight: 700; color: #4A9EFF; margin: 0;">
                    Welcome to CrawlMind
                </h1>
            </div>
            <p style="font-size: 1.2rem; color: #a0a0a0; margin: 0;">
                Professional AI Powered Document Analysis & Intelligence Platform
            </p>
        </div>
    """.format(
        st.session_state.get('logo_base64', '')
    ), unsafe_allow_html=True)
    
    render_user_profile_header()

    with st.sidebar:
        name = st.session_state.user_name or "User"
        image = st.session_state.user_image

        # Create base64 image if not a URL
        img_html = ""
        if image:
            if image.startswith('http'):
                img_html = f'<img src="{image}" style="width:60px;height:60px;border-radius:50%;border:2px solid #4A9EFF;box-shadow:0 0 10px rgba(74,158,255,0.4);">'
            else:
                img_html = f'<img src="data:image/png;base64,{image}" style="width:60px;height:60px;border-radius:50%;border:2px solid #4A9EFF;box-shadow:0 0 10px rgba(74,158,255,0.4);">'

        # Render profile header without dark box
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;height:10vh;">
                {img_html}
                <div>
                    <div style="font-weight: bold; font-size: 1.2em; margin-bottom: 5px; color: white;"> Welcome, {name}!</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()

        st.markdown("### 🔑 API Configuration")
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.gemini_api_key,
            placeholder="Get from Google AI Studio",
            help="Required for AI document analysis"
        )
        if gemini_key:
            st.session_state.gemini_api_key = gemini_key
            st.success("✅ API Key configured!")

        st.divider()

        st.markdown("### 📄 Document Sources")

        with st.expander("🌐 Web URLs", expanded=True):
            url_input = st.text_input("Enter URL", placeholder="https://example.com")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add URL", disabled=not validators.url(url_input) if url_input else True):
                    st.session_state.urls = [url_input]
                    st.success("✅ URL added")
            with col2:
                if st.button("Clear URLs"):
                    st.session_state.urls = []
                    st.success("✅ URLs cleared")

            if st.session_state.urls:
                url = st.session_state.urls[0]
                st.success(f"📁 Current URL: {url[:30]}..." if len(url) > 30 else f"📁 Current URL: {url}")

        with st.expander("📁 File Upload", expanded=True):
            uploaded_files = st.file_uploader(
                "Upload documents",
                type=["pdf", "txt"],
                accept_multiple_files=True,
                help="Upload PDF or text files for analysis"
            )

            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

        st.divider()
        if st.button("Crawl & Embed Documents", use_container_width=True, type="primary"):
            process_documents()
    
    # Main content area - Chat interface

    
    # Initialize chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Display chat messages
    for i, (role, message) in enumerate(st.session_state.chat_history):
        with st.chat_message(role):
            st.write(message)
            
    # Handle user input
    if user_input := st.chat_input("Ask anything about your documents...", key="user_chat_input"):
        # Add user message to chat history
        st.session_state.chat_history.append(("user", user_input))
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
            
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                try:
                    response = query_documents(user_input)
                    st.write(response)
                    # Add assistant response to chat history
                    st.session_state.chat_history.append(("assistant", response))
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    # Add error message to chat history
                    st.session_state.chat_history.append(("assistant", error_msg))

def generate_default_avatar(initials):
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        import random
        
        img_size = (200, 200)
        
        colors = [
            (74, 158, 255),
            (94, 234, 212),
            (162, 155, 254),
            (251, 150, 110),
            (251, 113, 133),
            (0, 184, 148),
            (253, 203, 110),
            (214, 48, 49)
        ]
        
        if initials:
            color_index = ord(initials[0].lower()) % len(colors)
        else:
            color_index = random.randint(0, len(colors) - 1)
            
        background_color = colors[color_index]
        text_color = (255, 255, 255)
        
        img = Image.new('RGB', img_size, background_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font_size = 80
            try:
                font = ImageFont.truetype("Arial", font_size)
            except:
                try:
                    font = ImageFont.truetype("Helvetica", font_size)
                except:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        try:
            text_width = draw.textlength(initials.upper(), font=font)
            text_height = font_size
            position = ((img_size[0] - text_width) / 2, (img_size[1] - text_height) / 2)
        except AttributeError:
            try:
                text_width, text_height = draw.textsize(initials.upper(), font=font)
                position = ((img_size[0] - text_width) / 2, (img_size[1] - text_height) / 2)
            except:
                position = (img_size[0] // 4, img_size[1] // 4)
        
        draw.text(position, initials.upper(), font=font, fill=text_color)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Error generating avatar: {e}")
        return None

def get_user_details_from_token(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Debug the token payload
        print("Token payload keys:", payload.keys())
        print("User ID:", payload.get('user_id', 'Not found') or payload.get('sub', 'Not found'))
        print("Email:", payload.get('email', 'Not found') or payload.get('primary_email_address', 'Not found'))
        print("Name:", payload.get('name', 'Not found'))
        print("First name:", payload.get('firstName', 'Not found') or payload.get('given_name', 'Not found'))
        print("Last name:", payload.get('lastName', 'Not found') or payload.get('family_name', 'Not found'))
        print("Image URL:", payload.get('image_url', 'Not found') or payload.get('picture', 'Not found'))
        
        # Extract email with fallbacks
        email = payload.get('email', '')
        if not email and 'primary_email' in payload:
            email = payload.get('primary_email')
        
        if payload.get('name'):
             name = payload.get('name')
        elif payload.get('firstName') and payload.get('lastName'):
            name = f"{payload.get('firstName')} {payload.get('lastName')}"
        elif payload.get('firstName'):
            name = payload.get('firstName')
        elif payload.get('given_name') and payload.get('family_name'):
            name = f"{payload.get('given_name')} {payload.get('family_name')}"
        elif payload.get('username'):
            name = payload.get('username')
        elif email:
            username = email.split('@')[0]
            name = ' '.join([part.capitalize() for part in username.split('.')])
        else:
            name = 'User'

                
        # Generate initials for avatar
        name_parts = name.split()
        if len(name_parts) >= 2:
            initials = name_parts[0][0] + name_parts[-1][0]
        elif len(name_parts) == 1 and name_parts[0]:
            initials = name_parts[0][0]
            if len(name_parts[0]) > 1:
                initials += name_parts[0][1]
        elif email:
            initials = email[0].upper()
        else:
            initials = 'U'
        
        # Store user details in session state
        st.session_state.user_email = email
        st.session_state.user_name = name
        
        # Look for profile image in various possible fields
        user_image = None
        for img_field in ['image_url', 'picture', 'profile_image_url', 'avatar_url', 'image']:
            if img_field in payload and payload.get(img_field):
                user_image = payload.get(img_field)
                break
        
        if user_image:
            st.session_state.user_image = user_image
        else:
            # Generate avatar from initials
            avatar = generate_default_avatar(initials)
            if avatar:
                st.session_state.user_image = avatar
            else:
                if st.session_state.default_avatar is None:
                    st.session_state.default_avatar = generate_default_avatar('U')
                st.session_state.user_image = st.session_state.default_avatar
        
        # Store additional user data if available
        if 'user_metadata' in payload:
            st.session_state.user_metadata = payload.get('user_metadata')
            
        return True
        
    except Exception as e:
        print(f"Error extracting user details: {e}")
        st.session_state.user_name = "User"
        
        if st.session_state.default_avatar is None:
            st.session_state.default_avatar = generate_default_avatar('U')
        
        st.session_state.user_image = st.session_state.default_avatar
        return False

def render_user_profile_header():
    if not st.session_state.authenticated:
        return
    
    # Ensure we have user details
    if st.session_state.jwt_token and (not st.session_state.user_name or st.session_state.user_name == "User"):
        get_user_details_from_token(st.session_state.jwt_token)
    
    # Get user details with fallbacks
    name = st.session_state.user_name or "User"
    email = st.session_state.user_email or ""
    image = st.session_state.user_image
    
    # Print debugging info to console
    print(f"DEBUG - User Profile: Name: {name}, Email: {email}, Has Image: {image is not None}")
    
    # Generate avatar if no image is available but we have a name
    if not image and name != "User":
        name_parts = name.split()
        if len(name_parts) >= 2:
            initials = name_parts[0][0] + name_parts[-1][0]
        elif len(name_parts) == 1 and name_parts[0]:
            initials = name_parts[0][0]
            if len(name_parts[0]) > 1:
                initials += name_parts[0][1]
        else:
            initials = 'U'
        
        # Generate and store avatar
        avatar = generate_default_avatar(initials)
        if avatar:
            st.session_state.user_image = avatar
            image = avatar
    
    # Create image tag based on image type
    img_tag = ""
    if image and image.startswith('http'):
        img_tag = f'<img src="{image}" class="profile-picture" alt="{name}">'
    elif image:
        img_tag = f'<img src="data:image/png;base64,{image}" class="profile-picture" alt="{name}">'
    else:
        img_tag = f'<div class="profile-picture-fallback">{name[0].upper()}</div>'
    
    # Format name for display
    display_name = name
    if len(name) > 15:
        display_name = f"{name[:12]}..."
    
    profile_html = f"""
    <div class="header-container">
        <div class="brand-logo">
            <img src="data:image/png;base64,{st.session_state.logo_base64}" class="header-logo" alt="CrawlMind Logo">
        </div>
        <div class="profile-container">
            <div class="user-profile" title="User Profile: {name}">
                {img_tag}
                <span class="user-name">{display_name}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke-width="2" class="dropdown-arrow">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="profile-dropdown">
                <div class="dropdown-item user-info">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    <div class="user-details">
                        <span class="user-fullname">{name}</span>
                        <span class="user-email">{email}</span>
                    </div>
                </div>
                <div class="dropdown-divider"></div>
                <a href="/?logout=true" class="dropdown-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    <span>Sign Out</span>
                </a>
            </div>
        </div>
    </div>
    """
    
    st.markdown(profile_html, unsafe_allow_html=True)
    
    # Add social links to the bottom right corner
    footer_social_html = """
    <div class="footer-social-links">
        <a href="https://github.com/Kaustub-Mocherla" target="_blank" class="social-button github" title="GitHub">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 10.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-.588 8.199-5.084 8.199-10.386 0-6.627-5.373-12-12-12z"/>
            </svg>
        </a>
        <a href="https://www.linkedin.com/in/kaustub-mocherla/" target="_blank" class="social-button linkedin" title="LinkedIn">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
        </a>
    </div>
    """
    st.markdown(footer_social_html, unsafe_allow_html=True)

def safe_clear_database(db_path):
    """Safely clear the ChromaDB database with retries and proper cleanup"""
    if not os.path.exists(db_path):
        return {"success": True, "message": "No existing database to clear"}
    
    try:
        # Force garbage collection to release any file handles
        gc.collect()
        
        for attempt in range(3):  # Try up to 3 times
            try:
                shutil.rmtree(db_path)
                return {"success": True, "message": "✅ Previous database cleared successfully"}
            except PermissionError:
                if attempt < 2:  # If not the last attempt
                    st.warning(f"⚠️ Database files in use. Retrying... (attempt {attempt + 1}/3)")
                    time.sleep(1)  # Wait a bit before retry
                    gc.collect()  # Try to free resources
                else:
                    # On last attempt failure, use a new path instead
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_path = f"{db_path}_{timestamp}"
                    st.warning(f"⚠️ Could not clear previous database. Using new path: {new_path}")
                    return {"success": True, "message": f"Using new database: {new_path}", "new_path": new_path}
    except Exception as e:
        st.error(f"❌ Database cleanup error: {str(e)}")
        # On error, use a new path to avoid conflicts
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_path = f"{db_path}_{timestamp}"
        return {"success": False, "message": f"Error: {str(e)}. Using new path: {new_path}", "new_path": new_path}

def main():
    initialize_session_state()
    
    query_params = st.query_params
    if 'logout' in query_params and query_params['logout'] == 'true':
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        initialize_session_state()
        st.query_params.clear()
        st.rerun()
    
    # Check for token in URL
    if 'token' in query_params and not st.session_state.authenticated:
        token = query_params['token']
        st.session_state.jwt_token = token
        st.session_state.auth_loading = True
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Display logo
            if st.session_state.logo_base64:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;"><img src="data:image/png;base64,{st.session_state.logo_base64}" class="auth-logo" alt="CrawlMind Logo" style="height:15vh; margin-right: 20px;width:15vh"><span style="font-size: 10vh; font-weight: bold; color: #4A9EFF;">CrawlMind</span></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2 class="auth-title" style = "display:flex;justify-content:center">Authenticating...</h2>', unsafe_allow_html=True)
            st.markdown('<div class="auth-loading"><div class="auth-loading-spinner"></div><div class="auth-loading-text">Verifying your credentials...</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Actually verify the token
        if verify_token_with_api(token):
            st.session_state.authenticated = True
            st.session_state.auth_loading = False
            st.query_params.clear()
            st.rerun()
        else:
            st.session_state.jwt_token = None
            st.session_state.auth_loading = False
            st.query_params.clear()
            st.rerun()
    
    # Check for existing token in session state
    elif st.session_state.jwt_token and not st.session_state.authenticated:
        st.session_state.auth_loading = True
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Display logo
            if st.session_state.logo_base64:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;"><img src="data:image/png;base64,{st.session_state.logo_base64}" class="auth-logo" alt="CrawlMind Logo" style="height:15vh; margin-right: 20px;width:15vh"><span style="font-size: 10vh; font-weight: bold; color: #4A9EFF;">CrawlMind</span></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2 class="auth-title" style = "display:flex;justify-content:center">Authenticating...</h2>', unsafe_allow_html=True)
            st.markdown('<div class="auth-loading"><div class="auth-loading-spinner"></div><div class="auth-loading-text">Verifying your credentials...</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        if verify_token_with_api(st.session_state.jwt_token):
            st.session_state.authenticated = True
            st.session_state.auth_loading = False
            st.rerun()
        else:
            st.session_state.jwt_token = None
            st.session_state.auth_loading = False
            st.rerun()
    
    # If auth is loading, show the loading screen
    elif st.session_state.auth_loading:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            # Display logo
            if st.session_state.logo_base64:
                st.markdown(f'<div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;"><img src="data:image/png;base64,{st.session_state.logo_base64}" class="auth-logo" alt="CrawlMind Logo" style="height:15vh; margin-right: 20px;width:15vh"><span style="font-size: 10vh; font-weight: bold; color: #4A9EFF;">CrawlMind</span></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<h2 class="auth-title" style = "display:flex;justify-content:center">Authenticating...</h2>', unsafe_allow_html=True)
            st.markdown('<div class="auth-loading"><div class="auth-loading-spinner"></div><div class="auth-loading-text">Verifying your credentials...</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # If not authenticated, show login screen
    elif not st.session_state.authenticated:
        show_auth_required()
        return
    
    # Show main app if authenticated
    else:
        show_main_app()

if __name__ == "__main__":
    main()
