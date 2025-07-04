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
        background-color: #000000;
        color: #ffffff;
    }
    .stSidebar {
        background-color: #1a0000;
    }
    .stButton > button {
        background-color: #dc2626;
        color: white;
        border: 1px solid #dc2626;
    }
    .stButton > button:hover {
        background-color: #b91c1c;
        border: 1px solid #b91c1c;
    }
    .stTextInput > div > div > input {
        background-color: #1a0000;
        color: white;
        border: 1px solid #dc2626;
    }
    .stSelectbox > div > div > div {
        background-color: #1a0000;
        color: white;
    }
    .stRadio > div {
        background-color: #1a0000;
    }
    .stExpander {
        background-color: #1a0000;
        border: 1px solid #dc2626;
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
        st.markdown("### 🔴 CrawlMind")
        st.caption("AI ASSISTANT")
    
    st.divider()
    
    st.markdown("**Select Mode:**")
    mode = st.radio(
        "Choose your mode:",
        ["Latest Updates", "Chat with CrawlMind"],
        key="mode_selector",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if mode == "Chat with CrawlMind":
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
    
    else:
        st.markdown("### 📰 Latest Updates")
        st.info("Feature coming soon! This will show the latest updates about CrawlMind.")
        
        st.divider()
        st.markdown("### 🎯 Basic Interactions")
        st.markdown("**• Ask About CrawlMind:** Type your questions about CrawlMind features")
        st.markdown("**• Document Analysis:** Upload files for AI analysis")  
        st.markdown("**• Web Crawling:** Enter URLs to extract and analyze content")

st.title("🔴 CrawlMind Assistant")
st.caption("Hello! How can I assist you with your documents today?")

chat_container = st.container()

if st.session_state.collection is None:
    with chat_container:
        st.info("👋 Welcome to CrawlMind! Use the sidebar to add URLs or upload files, then click 'Crawl & Embed' to get started.")
        st.markdown("""
        ### Getting Started:
        1. **Add Content**: Use the sidebar to add URLs or upload documents
        2. **Process**: Click "Crawl & Embed" to analyze your content  
        3. **Chat**: Ask questions about your documents
        """)
else:
    with chat_container:
        if not st.session_state.chat_history:
            st.success("✅ Ready to chat! Your documents have been processed. Ask me anything!")
        
        for user_msg, ai_msg in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(user_msg)
            with st.chat_message("assistant"):
                st.write(ai_msg)

if st.session_state.collection is not None:
    if user_input := st.chat_input("Ask me about your documents..."):
        st.session_state.chat_history.append((user_input, ""))
        
        with st.spinner("Thinking..."):
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
else:
    st.info("Please add and process documents first using the sidebar.")

st.markdown("---")
st.caption("💡 Tip: You can process multiple URLs and files together for comprehensive document analysis!")
