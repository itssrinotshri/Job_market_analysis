@echo off
TITLE Data Analyst Job Market Analysis - Launcher
echo ===================================================================
echo 🚀 Launching Data Analyst Job Market Interactive Dashboard...
echo ===================================================================
echo.
cd /d "%~dp0"

python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Streamlit is not installed. Installing required dependencies...
    pip install -r requirements.txt streamlit pandas
)

echo Starting Web Dashboard on http://localhost:8501 ...
python run.py web

pause
