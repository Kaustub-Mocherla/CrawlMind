@echo off
echo ================================================
echo        CrawlMind Clerk App Setup Script
echo ================================================

echo.
echo Step 1: Installing Node.js dependencies...
cd /d "c:\Users\kaustubchandra\Desktop\CrawlMind-master\my-clerk-app"
call npm install

echo.
echo Step 2: Setting up environment variables...
echo Please configure your .env.local file with your Clerk keys:
echo - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
echo - CLERK_SECRET_KEY
echo.
echo You can get these from: https://dashboard.clerk.com/

echo.
echo Step 3: Building the application...
call npm run build

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo To start the development server:
echo   cd my-clerk-app
echo   npm run dev
echo.
echo The app will be available at: http://localhost:3000
echo.
echo Make sure to:
echo 1. Configure your Clerk keys in .env.local
echo 2. Set up your Clerk application URLs in the Clerk dashboard
echo 3. Start your FastAPI backend (port 8000)
echo 4. Start your Streamlit app (port 8501)
echo.
pause
