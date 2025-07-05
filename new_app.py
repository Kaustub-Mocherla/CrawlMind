import os
import sys
import subprocess
import tempfile
import uuid

import streamlit as st
import validators

from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader

st.set_page_config(
    page_title="CrawlMind", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    .stSidebar {
        background-color: #1a1a1a;
        border-right: 1px solid #333;
    }
    .stButton > button {
        background-color: #4A9EFF;
        color: white;
        border: 1px solid #4A9EFF;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3b82f6;
        border: 1px solid #3b82f6;
        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
    }
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #404040;
        border-radius: 8px;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4A9EFF;
        box-shadow: 0 0 0 1px #4A9EFF;
    }
    .stSelectbox > div > div > div {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #404040;
        border-radius: 8px;
    }
    .stRadio > div {
        background-color: transparent;
    }
    .stExpander {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stExpander > div > div > div > div {
        background-color: #1a1a1a;
    }
    .stFileUploader > div > div {
        background-color: #2d2d2d;
        border: 2px dashed #404040;
        border-radius: 8px;
        transition: border-color 0.3s ease;
    }
    .stFileUploader > div > div:hover {
        border-color: #4A9EFF;
    }
    .stChatInput > div {
        max-width: 1200px;
        margin: 0 auto;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
    }
    .stChatInput textarea {
        font-size: 18px !important;
        padding: 20px 25px !important;
        min-height: 60px !important;
        line-height: 1.4 !important;
        transition: all 0.3s ease !important;
        flex: 1;
    }
    .stChatInput button {
        width: 50px !important;
        height: 50px !important;
        margin-left: 15px !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #4A9EFF !important;
        border: none !important;
        color: white !important;
        font-size: 20px !important;
    }
    .stChatInput button:hover {
        background-color: #3b82f6 !important;
        transform: scale(1.05) !important;
    }
    .stChatInput button svg {
        width: 20px !important;
        height: 20px !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff;
    }
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        border: 1px solid #22c55e;
        color: #22c55e;
        border-radius: 8px;
    }
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        color: #ef4444;
        border-radius: 8px;
    }
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        color: #f59e0b;
        border-radius: 8px;
    }
    .stInfo {
        background-color: rgba(74, 158, 255, 0.1);
        border: 1px solid #4A9EFF;
        color: #4A9EFF;
        border-radius: 8px;
    }
    div[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    .stSpinner > div {
        border-top-color: #4A9EFF !important;
    }
    </style>
""", unsafe_allow_html=True)

if "urls" not in st.session_state:
    st.session_state.urls = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "collection" not in st.session_state:
    st.session_state.collection = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("artificial-intelligence.png", width=60)
    with col2:
        st.markdown("### CrawlMind")
        st.caption("AI ASSISTANT")
    
    st.divider()
    
    st.markdown("### 🔧 Document Setup")
    
    with st.expander("🌐 Add URL", expanded=True):
        new_url = st.text_input(
            "Enter URL", 
            placeholder="https://example.com",
            key="url_input"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Set URL", key="add_url_btn", use_container_width=True):
                if validators.url(new_url):
                    st.session_state.urls = [new_url]
                    st.success("URL set!")
                    st.rerun()
                else:
                    st.error("Invalid URL.")
        
        with col2:
            if st.button("Clear URL", key="clear_urls_btn", use_container_width=True):
                st.session_state.urls = []
                st.rerun()

        if st.session_state.urls:
            st.markdown("**📋 Current URL:**")
            url = st.session_state.urls[0]
            st.text(f"• {url[:60]}..." if len(url) > 60 else f"• {url}")

    with st.expander("📁 Upload Documents", expanded=True):
        uploaded_docs = st.file_uploader(
            "Choose files",
            type=["txt", "pdf"],
            accept_multiple_files=True,
            help="Upload TXT or PDF files to analyze",
            key="file_uploader"
        )
        if uploaded_docs:
            st.session_state.uploaded_files = uploaded_docs
            st.success(f"Uploaded {len(uploaded_docs)} file(s)")

    st.divider()
    if st.button("🚀 Crawl & Embed", key="crawl_embed_btn", use_container_width=True, type="primary"):
        with st.spinner("Processing documents..."):
            chroma_client = PersistentClient(path="./crawlmind_db")
            try:
                chroma_client.delete_collection("crawlmind_collection")
            except:
                pass

            collection = chroma_client.get_or_create_collection(name="crawlmind_collection")

            embedding_function = OllamaEmbeddings(
                model="llama3.1:latest",
                base_url="http://localhost:11434"
            )

            all_chunks = []

            for url in st.session_state.urls:
                subprocess.run([sys.executable, "crawler.py", url])
                if os.path.exists("crawled_content.md"):
                    with open("crawled_content.md", "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        if text:
                            all_chunks.append(text)

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
            for chunk in all_chunks:
                emb = embedding_function.embed_query(chunk)
                embeddings.append(emb)
                ids.append(str(uuid.uuid4()))
                valid_chunks.append(chunk)

            if valid_chunks:
                collection.add(documents=valid_chunks, embeddings=embeddings, ids=ids)
                st.session_state.collection = collection
                st.success(f"✅ Embedded {len(valid_chunks)} chunks.")
            else:
                st.warning("No valid chunks found!")

# Load and encode the logo for the main title
import base64
if 'logo_base64' not in st.session_state:
    try:
        with open("artificial-intelligence.png", "rb") as img_file:
            st.session_state.logo_base64 = base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.session_state.logo_base64 = ""

st.markdown("""
    <div style="text-align: center; margin: 2rem 0; margin-bottom: 4rem;">
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{}" style="width: 80px; height: 80px; margin-right: 20px;" alt="CrawlMind Logo">
            <h1 style="font-size: 3.5rem; font-weight: 700; color: #4A9EFF; margin: 0;">
                Welcome to CrawlMind
            </h1>
        </div>
        <p style="font-size: 1.2rem; color: #a0a0a0; margin: 0;">
            Professional AI-Powered Document Analysis & Intelligence Platform
        </p>
    </div>
""".format(
    st.session_state.get('logo_base64', '')
), unsafe_allow_html=True)



if st.session_state.chat_history:
    for user_msg, ai_msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(user_msg)
        with st.chat_message("assistant"):
            st.write(ai_msg)

if user_input := st.chat_input("Enter your message here... Ask me anything about your documents!"):
    if st.session_state.collection is None:
        st.error("⚠️ Please upload documents and click 'Crawl & Embed' first!")
    else:
        st.session_state.chat_history.append((user_input, ""))
        
        with st.spinner("Processing your query..."):
            embedding_function = OllamaEmbeddings(
                model="llama3.1:latest",
                base_url="http://localhost:11434"
            )

            db = Chroma(
                client=PersistentClient(path="./crawlmind_db"),
                collection_name="crawlmind_collection",
                embedding_function=embedding_function
            )
            retriever = db.as_retriever()
            llm = OllamaLLM(model="llama3.1:latest", base_url="http://localhost:11434")

            docs = retriever.invoke(user_input)
            context = "\n\n".join([doc.page_content for doc in docs]) or "No relevant context found."

            rag_prompt = PromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the retrieved context below to answer the question.
If you don't know, say you don't know.

Context:
{context}

Question:
{question}

Answer in 2-3 clear sentences.
""")

            final_prompt = rag_prompt.format(
                context=context,
                question=user_input
            )

            answer = llm.invoke(final_prompt)
            
            st.session_state.chat_history[-1] = (user_input, answer)
            st.rerun()
