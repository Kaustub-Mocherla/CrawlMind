# CrawlMind PowerShell Launcher

## Quick Start with PowerShell Script

The easiest way to start all CrawlMind services is using the PowerShell launcher:

```powershell
# Start all services (recommended)
.\start-all-services.ps1

# Or with options
.\start-all-services.ps1 -SkipPortCheck -NoVenv
```

### What it does:
✅ **Validates requirements** - Checks Python, Node.js, npm availability  
✅ **Checks ports** - Ensures ports 3000, 8000, 8501 are available  
✅ **Activates Python venv** - If `app/` virtual environment exists  
✅ **Starts services** - Launches each in separate PowerShell windows:
- **FastAPI Backend** → `http://localhost:8000`
- **Streamlit App** → `http://localhost:8501` 
- **Next.js Clerk App** → `http://localhost:3000`

### Parameters:
- `-SkipPortCheck` - Skip port availability validation
- `-NoVenv` - Skip Python virtual environment activation

### Getting Help:
```powershell
Get-Help .\start-all-services.ps1 -Detailed
```

## Manual Service Start (Alternative)

If you prefer to start services manually:

```powershell
# Terminal 1: FastAPI Backend
cd fastapi_app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Streamlit App  
cd streamlit_app
streamlit run app_combined.py --server.port 8501

# Terminal 3: Next.js Frontend
cd my-clerk-app
npm run dev
```

## Troubleshooting the PowerShell Script

### Port Conflicts
```powershell
# Find what's using the port
netstat -ano | findstr :8000
# Kill the process
taskkill /PID [PID] /F
```

### Missing Dependencies
```powershell
# Install Python packages
pip install -r requirements.txt

# Install Node.js packages
cd my-clerk-app && npm install
```

The PowerShell script provides detailed error messages and troubleshooting guidance for common issues.