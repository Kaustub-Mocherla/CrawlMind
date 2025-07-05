<div align="center">
  <img src="artificial-intelligence.png" alt="CrawlMind Logo" width="160" height="160">
  
  #  CrawlMind
  
  **A powerful AI-powered document analysis and chat application**
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
  ![License](https://img.shields.io/badge/License-MIT-green.svg)
  ![AI](https://img.shields.io/badge/AI-Powered-orange.svg)
</div>

---

A powerful AI-powered document analysis and chat application built with Streamlit. CrawlMind allows you to crawl web content, upload documents, and interact with your data using advanced RAG (Retrieval Augmented Generation) technology.

## ✨ Features

- **🌐 Web Crawling**: Extract content from any URL
- **📁 Document Upload**: Support for PDF and TXT files
- **🤖 AI Chat Interface**: Natural language interaction with your documents
- **🔍 RAG Technology**: Advanced retrieval-augmented generation using ChromaDB and LangChain
- **🎨 Modern UI**: Clean, dark-themed interface with red accent colors
- **⚡ Real-time Processing**: Instant document embedding and retrieval

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: Ollama, LangChain
- **Vector Database**: ChromaDB
- **Document Processing**: PyPDF, TextLoader
- **Web Crawling**: Custom crawler
- **Embeddings**: Ollama Embeddings (llama3.1)
- **LLM**: Ollama (llama3.1:latest)

## 📋 Prerequisites

Before running CrawlMind, ensure you have:

1. **Python 3.8+** installed
2. **Ollama** installed and running locally
3. **llama3.1:latest** model downloaded in Ollama

### Installing Ollama

```bash
# Download and install Ollama from https://ollama.ai
# Then pull the required model:
ollama pull llama3.1:latest
```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crawlmind.git
   cd crawlmind
   ```

2. **Create virtual environment**
   ```bash
   python -m venv app
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   app\Scripts\activate
   
   # macOS/Linux
   source app/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start Ollama service**
   ```bash
   ollama serve
   ```

6. **Run the application**
   ```bash
   streamlit run new_app.py
   ```

## 📦 Dependencies

```txt
streamlit
validators
chromadb
langchain-chroma
langchain-ollama
langchain-core
langchain-community
pypdf
```

## 🎮 Usage

### 1. Start the Application
Navigate to `http://localhost:8501` after running the Streamlit command.

### 2. Choose Mode
- **Latest Updates**: View upcoming features (coming soon)
- **Chat with CrawlMind**: Main functionality for document analysis

### 3. Add Content
- **URL**: Enter a single URL to crawl web content
- **Documents**: Upload PDF or TXT files

### 4. Process Documents
Click "🚀 Crawl & Embed" to process your content and create embeddings.

### 5. Chat with Your Data
Once processed, use the chat interface to ask questions about your documents.

## 📁 Project Structure

```
CrawlMind/
├── new_app.py              # Main Streamlit application
├── crawler.py              # Web crawling functionality
├── requirements.txt        # Python dependencies
├── artificial-intelligence.png  # App logo
├── crawled_content.md      # Temporary crawled content
├── crawlmind_db/          # ChromaDB storage
└── app/                   # Virtual environment
```

## 🔧 Configuration

### Ollama Settings
- **Base URL**: `http://localhost:11434`
- **Model**: `llama3.1:latest`
- **Embedding Model**: `llama3.1:latest`

### ChromaDB Settings
- **Storage Path**: `./crawlmind_db`
- **Collection Name**: `crawlmind_collection`

## 🎨 UI Theme

CrawlMind features a sleek red and black theme:
- **Background**: Pure black (#000000)
- **Sidebar**: Dark red (#1a0000)
- **Accent**: Red (#dc2626)
- **Typography**: Clean, modern fonts

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Known Issues

- Ensure Ollama service is running before starting the application
- Large documents may take time to process
- UTF-8 encoding is required for web content with special characters

## 🚀 Roadmap

- [ ] Support for more document formats (DOCX, HTML)
- [ ] Multiple LLM provider support
- [ ] Advanced search and filtering
- [ ] Document summarization features
- [ ] Export chat conversations
- [ ] User authentication and sessions

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/crawlmind/issues) page
2. Create a new issue with detailed description
3. Include error logs and system information

## ⭐ Acknowledgments

- [Streamlit](https://streamlit.io/) - For the amazing web framework
- [Ollama](https://ollama.ai/) - For local LLM capabilities
- [LangChain](https://langchain.com/) - For RAG implementation
- [ChromaDB](https://www.trychroma.com/) - For vector storage

---

Made with ❤️ by Mocherla Chandra Kaustub
