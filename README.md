  ```
                     ___          
               ______                    ____  ____           __
              / ____/________ __      __/ /  |/  (_)___  ____/ /
             / /   / ___/ __ `/ | /| / / / /|_/ / / __ \/ __  / 
            / /___/ /  / /_/ /| |/ |/ / / /  / / / / / / /_/ /  
            \____/_/   \__,_/ |__/|__/_/_/  /_/_/_/ /_/\__,_/

                                                                      
                                                                                    
```
<p align="center">
  <img src="artificial-intelligence.png" alt="CrawlMind Logo" width="200" height="200">
</p>

A **production-ready** AI-powered document analysis platform with **Clerk authentication**, **Framer Motion animations**, and a **modern dark theme** combining Next.js, FastAPI, and Streamlit for a complete RAG (Retrieval Augmented Generation) solution.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg) ![Next.js](https://img.shields.io/badge/Next.js-15.3.5+-black.svg) ![Clerk](https://img.shields.io/badge/Clerk-5.7.5+-purple.svg) ![Framer Motion](https://img.shields.io/badge/Framer%20Motion-12.23.5+-pink.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

##  **System Architecture**          

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │───▶│  Streamlit UI   │───▶│  FastAPI RAG    │
│ (Clerk + Themes)│    │ (JWT Protected) │    │ (JWT Verified)  │
│ Framer Motion   │    │  Custom Styled  │    │   AI Backend    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   ChromaDB +    │
         │                       │              │   Google Gemini │
         │                       │              │   Vector Store  │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
 JWT Token Flow          Document Processing
 Dark Theme UI           AI Chat Interface
```

## **Features**

### **Modern UI/UX**
- **Dark Theme** - Sleek black interface with #4A9EFF blue accents
- **Framer Motion** - Smooth animations and transitions
- **Responsive Design** - Tailwind CSS with mobile-first approach
- **Interactive Elements** - Hover effects and spring animations

### **Enterprise Authentication**
- **Clerk Integration** - Enterprise-grade user management
- **JWT Tokens** - Secure authentication flow
- **User Profiles** - Complete profile management
- **Protected Routes** - Secure access control

### **AI-Powered Features**
- **Document Processing** - PDF, TXT, DOCX, PPTX support
- **Advanced Web Crawling** - JavaScript execution and CSS selectors
- **AI Chat Interface** - Query documents with Google Gemini
- **Vector Search** - ChromaDB with semantic search
- **RAG Pipeline** - Retrieval Augmented Generation

## 🛠️ **Tech Stack**

### **Frontend**
- **Next.js 15.3.5** - React framework with App Router
- **TypeScript 5.8.3** - Type-safe development
- **Tailwind CSS 3.4.17** - Utility-first styling
- **Framer Motion 12.23.5** - Advanced animations
- **Lucide React 0.525.0** - Modern icons

### **Authentication**
- **Clerk 5.7.5** - Enterprise-grade JWT authentication
- **JWT Tokens** - Secure session management

### **Backend**
- **FastAPI 0.115.6** - High-performance Python API
- **Streamlit 1.41.0** - Interactive data apps
- **Uvicorn 0.32.1** - ASGI server

### **AI/ML**
- **Google Gemini** - Large Language Model (gemini-1.5-flash)
- **LangChain 0.3.10** - AI application framework
- **ChromaDB 0.5.23** - Vector database
- **Crawl4AI 0.2.77** - Advanced web crawling

## 📋 **Quick Start**

### **Prerequisites**

- **Node.js 18+** (for Next.js frontend)
- **Python 3.13+** (for FastAPI/Streamlit backend)
- **Clerk Account** ([clerk.com](https://clerk.com))
- **Google Gemini API** ([makersuite.google.com](https://makersuite.google.com/app/apikey))

### **1. Clone & Setup**

```bash
git clone https://github.com/your-username/CrawlMind.git
cd CrawlMind

# Copy environment template
cp .env.example .env
```

### **2. Configure Environment Variables**

Create `.env` in the root directory:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
CLERK_JWKS_URL=https://your-clerk-domain.clerk.accounts.dev/.well-known/jwks.json
CLERK_AUDIENCE=your-clerk-audience

# AI Configuration  
GEMINI_API_KEY=your_gemini_api_key_here

# Service URLs
FASTAPI_URL=http://localhost:8000
STREAMLIT_URL=http://localhost:8501
NEXTJS_URL=http://localhost:3000
```

Create `my-clerk-app/.env.local`:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard
```

### **3. Install Dependencies**

```bash
# Install Python dependencies (virtual environment recommended)
python -m venv app
app\Scripts\activate  # Windows
# source app/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Install Next.js dependencies
cd my-clerk-app
npm install
cd ..
```

### **4. Configure Clerk JWT Template**

**Important**: Set up JWT template in Clerk Dashboard for secure authentication.

1. **Clerk Dashboard** → Configure → Sessions → JWT Templates
2. **Create New Template**:
   - **Name**: `crawlmind_backend`
   - **Token lifetime**: 3600 seconds (1 hour)
   - **Claims** (exact JSON payload):
   ```json
   {
     "user_id": "{{user.id}}",
     "email": "{{user.primary_email_address.email_address}}",
     "name": "{{user.first_name}} {{user.last_name}}",
     "firstName": "{{user.first_name}}",
     "lastName": "{{user.last_name}}",
     "image_url": "{{user.image_url}}",
     "picture": "{{user.image_url}}"
   }
   ```

** Important Notes**: 
- Do NOT include reserved claims (`iss`, `aud`, `exp`, `iat`, `nbf`)
- Clerk handles JWT validation automatically
- Keep payload minimal for performance

### **5. Start All Services**

**Option A: Manual Start (Recommended for Development)**

```bash
# Terminal 1: Start Next.js Frontend
cd my-clerk-app
npm run dev
# → http://localhost:3000

# Terminal 2: Start FastAPI Backend
cd fastapi_app
python main.py
# → http://localhost:8000

# Terminal 3: Start Streamlit App
cd streamlit_app
streamlit run app.py
# → http://localhost:8501
```

**Option B: PowerShell Script (Windows)**

```powershell
# Start all services with single command
.\start-all-services.ps1
```

This script will:
- Check if required ports are available
- Activate the Python virtual environment (if found)
- Start FastAPI backend, Streamlit app, and Next.js server in separate windows
- Monitor the status of all services
- Display important JWT template configuration information

Alternatively, you can start each service manually:

**Terminal 1: Start FastAPI Backend**
```powershell
cd fastapi_app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2: Start Streamlit App**
```powershell
cd streamlit_app
streamlit run app_combined.py --server.port 8501
```

**Terminal 3: Start Next.js Clerk App**
```powershell
cd my-clerk-app
npm run dev
```

You can also check the status of your services anytime with:

```powershell
python check_services.py
# or monitor continuously
python check_services.py --watch
```

### **6. Access Applications**

- **Next.js Frontend**: http://localhost:3000 - Start here for authentication
- **Streamlit App**: Accessed through Next.js dashboard (don't open directly)
- **FastAPI Backend**: http://localhost:8000 (API backend)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

##  **User Flow**

1. **Sign Up/In** at http://localhost:3000 using Clerk
2. **Access Dashboard** and click "Launch CrawlMind AI Assistant" 
3. **JWT Token** is automatically passed to Streamlit app
4. **Upload Documents** or add URLs in the sidebar
5. **Click "Crawl & Embed"** to process documents
6. **Start Chatting** with your AI assistant!

##  **API Endpoints**

### **FastAPI Backend** (`http://localhost:8000`)

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/extract` | Extract text from uploaded documents | JWT Required |
| `POST` | `/embed` | Generate embeddings for documents | JWT Required |
| `POST` | `/query` | Query documents with AI | JWT Required |
| `POST` | `/crawl` | Crawl and process URLs | JWT Required |
| `GET` | `/health` | Health check endpoint | Public |
| `GET` | `/docs` | Interactive API documentation | Public |

### **Authentication Headers**
```bash
Authorization: Bearer <jwt_token_from_clerk>
Content-Type: application/json
```

## **UI Features**

### **Modern Dark Theme**
- **Color Scheme**: `#4A9EFF` blue accents on black background
- **Typography**: Clean, modern fonts with proper hierarchy
- **Animations**: Framer Motion for smooth transitions
- **Responsive**: Mobile-first design with Tailwind CSS

### **Interactive Elements**
- **Hover Effects**: Subtle animations on buttons and cards
- **Loading States**: Skeleton loaders and progress indicators
- **Toast Notifications**: Success/error feedback
- **Modal Dialogs**: Clean popup interfaces

##  **Development**

### **Project Structure**
```
CrawlMind/
├── my-clerk-app/          # Next.js Frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   └── public/          # Static assets
├── fastapi_app/          # Python Backend
│   ├── main.py          # FastAPI application
│   └── auth_clerk.py    # JWT authentication
├── streamlit_app/        # Streamlit UI
│   ├── app.py           # Main Streamlit app
│   └── crawlmind_db/    # ChromaDB storage
└── requirements.txt      # Python dependencies
```

### **Key Components**

#### **Frontend (Next.js)**
- `app/page.tsx` - Landing page with auth
- `app/dashboard/page.tsx` - Main dashboard with animations
- `app/globals.css` - Global styles and theme

#### **Backend (FastAPI)**
- `main.py` - API routes and JWT validation
- `auth_clerk.py` - Clerk JWT verification

#### **UI (Streamlit)**
- `app.py` - Interactive document chat interface

##  **Troubleshooting**

### **Common Issues**

#### **1. "Module not found" errors**
```bash
# Ensure virtual environment is activated
app\Scripts\activate  # Windows
source app/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### **2. "Port already in use"**
```bash
# Windows - Kill process on port
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

#### **3. JWT Authentication failures**
- Verify Clerk JWT template is configured correctly
- Check environment variables in both `.env` and `my-clerk-app/.env.local`
- Ensure JWKS URL matches your Clerk instance

#### **4. ChromaDB/Vector store issues**
```bash
# Clear and recreate database
rm -rf streamlit_app/crawlmind_db/
# Restart Streamlit app
```

### **Debug Mode**

Enable debug logging by setting:
```env
DEBUG=true
LOG_LEVEL=debug
```

##  **Contributing**

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### **Development Guidelines**

- Follow **TypeScript** best practices for frontend
- Use **Black** formatter for Python code
- Add **tests** for new features
- Update **documentation** for API changes
- Maintain **consistent** coding style

### **Code Standards**

```bash
# Python formatting
black .
flake8 .

# TypeScript/JavaScript
npm run lint
npm run type-check
```

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

##  **Acknowledgments**

- **Clerk** - Enterprise authentication platform
- **Google Gemini** - Advanced AI language model
- **ChromaDB** - Vector database for embeddings
- **Crawl4AI** - Intelligent web crawling
- **Streamlit** - Rapid UI development
- **Next.js** - React framework
- **FastAPI** - High-performance Python API framework

##  **Support**

- **Issues**: [GitHub Issues](https://github.com/your-username/CrawlMind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/CrawlMind/discussions)
- **Email**: support@crawlmind.ai

## **Deployment**

### **Production Deployment**

1. **Environment Setup**
   ```bash
   # Set production environment variables
   NODE_ENV=production
   ENVIRONMENT=production
   ```

2. **Build Frontend**
   ```bash
   cd my-clerk-app
   npm run build
   npm start
   ```

3. **Deploy Backend**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up --build -d
```

---

<p align="center">Made with ❤️ by the CrawlMind Team</p>
#
