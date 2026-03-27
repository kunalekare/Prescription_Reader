@echo off
REM Quick test launcher for Windows

echo ============================================
echo   PRESCRIPTION READER - QUICK TEST
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/3] Checking setup...
python test_setup.py
echo.

echo [2/3] Testing OCR API...
python quick_test.py
echo.

echo [3/3] Launching demo interface...
echo.
echo Starting Streamlit demo in 3 seconds...
echo Press Ctrl+C to cancel...
timeout /t 3 /nobreak >nul

streamlit run demo_ocr.py

pause
