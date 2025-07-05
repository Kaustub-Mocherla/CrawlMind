import os
import sys
import subprocess
import tempfile
import uuid

import streamlit as st
import validators
import google.generativeai as genai

from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader

st.set_page_config(
    page_title="CrawlMind", 
    page_icon="🔵", 
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('styles.css')


if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

with st.sidebar:
    st.markdown("### API Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        help="Enter your Google Gemini API key",
        placeholder="Enter your API key here..."
    )
    if api_key and api_key.strip():
        st.session_state.gemini_api_key = api_key.strip()
        genai.configure(api_key=api_key.strip())
        st.success("✅ API Key configured!")
    else:
        st.warning("⚠️ Please enter your Gemini API key")
        st.info("💡 Get your API key from: https://makersuite.google.com/app/apikey")
    
    st.divider()


st.markdown("""
    <div class="social-buttons">
        <a href="https://github.com/Kaustub-Mocherla" target="_blank" class="social-button github" title="GitHub">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 10.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-.588 8.199-5.084 8.199-10.386 0-6.627-5.373-12-12-12z"/>
            </svg>
        </a>
        <a href="https://www.linkedin.com/in/kaustub-mocherla/" target="_blank" class="social-button linkedin" title="LinkedIn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
        </a>
    </div>
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
    
    st.markdown("### Document Setup")
    
    with st.expander(" Add URL", expanded=True):
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
            st.markdown("** Current URL:**")
            url = st.session_state.urls[0]
            st.text(f"• {url[:60]}..." if len(url) > 60 else f"• {url}")

    with st.expander(" Upload Documents", expanded=True):
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
    if st.button(" Crawl & Embed", key="crawl_embed_btn", use_container_width=True, type="primary"):
        if not st.session_state.gemini_api_key or st.session_state.gemini_api_key.strip() == "":
            st.error("❌ Please enter your Gemini API key first!")
        elif not st.session_state.urls and not st.session_state.uploaded_files:
            st.error("❌ Please add a URL or upload documents first!")
        else:
            with st.spinner("Processing documents..."):
                chroma_client = PersistentClient(path="./crawlmind_db")
                try:
                    chroma_client.delete_collection("crawlmind_collection")
                except:
                    pass

                collection = chroma_client.get_or_create_collection(name="crawlmind_collection")

                embedding_function = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=st.session_state.gemini_api_key
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
                try:
                    for chunk in all_chunks:
                        emb = embedding_function.embed_query(chunk)
                        embeddings.append(emb)
                        ids.append(str(uuid.uuid4()))
                        valid_chunks.append(chunk)
                except Exception as e:
                    if "API_KEY_INVALID" in str(e):
                        st.error("❌ Invalid API key! Please check your Gemini API key.")
                        st.info("💡 Get a valid API key from: https://makersuite.google.com/app/apikey")
                    else:
                        st.error(f"❌ Error processing documents: {str(e)}")
                    st.stop()

                if valid_chunks:
                    collection.add(documents=valid_chunks, embeddings=embeddings, ids=ids)
                    st.session_state.collection = collection
                    st.success(f"Embedded {len(valid_chunks)} chunks.")
                else:
                    st.warning("No valid chunks found!")

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
            Professional AI Powered Document Analysis & Intelligence Platform
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

if user_input := st.chat_input("Enter your message here..."):
    if not st.session_state.gemini_api_key or st.session_state.gemini_api_key.strip() == "":
        st.error("❌ Please enter your Gemini API key first!")
    elif st.session_state.collection is None:
        st.error("❌ Please upload documents and click 'Crawl & Embed' first!")
    else:
        st.session_state.chat_history.append((user_input, ""))
        
        with st.spinner("Processing your query..."):
            embedding_function = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=st.session_state.gemini_api_key
            )

            db = Chroma(
                client=PersistentClient(path="./crawlmind_db"),
                collection_name="crawlmind_collection",
                embedding_function=embedding_function
            )
            retriever = db.as_retriever()
            llm = GoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=st.session_state.gemini_api_key,
                temperature=0.3
            )

            docs = retriever.invoke(user_input)
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
                question=user_input
            )

            answer = llm.invoke(final_prompt)
            
            st.session_state.chat_history[-1] = (user_input, answer)
            st.rerun()
