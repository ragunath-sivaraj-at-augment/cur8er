@echo off
REM Startup script for Cur8er (Windows)

echo 🎨 Cur8er - Startup Script
echo =================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version') do echo 📍 Python version: %%i

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔨 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🚀 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo 📝 Please edit .env file and add your API keys before running the app.
)

REM Start the application
echo 🎬 Starting Cur8er...
echo 🌐 The app will open in your default browser
echo 📺 Access the app at: http://localhost:8501
echo.
streamlit run app.py

pause