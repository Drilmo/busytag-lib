@echo off
REM BusyTag Demo Launcher for Windows

echo.
echo 🏷️  Starting BusyTag Demo Application...
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit is not installed!
    echo.
    echo Please install it with:
    echo   uv pip install streamlit pillow
    echo.
    echo Or install the demo extras:
    echo   uv pip install -e ".[demo]"
    echo.
    pause
    exit /b 1
)

REM Check if busytag library is importable
python -c "import sys; sys.path.insert(0, '..'); import busytag" 2>nul
if errorlevel 1 (
    echo ⚠️  Warning: BusyTag library might not be installed properly
    echo.
)

echo 🚀 Launching demo at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Launch streamlit
streamlit run app.py --browser.gatherUsageStats false --server.headless false --theme.base light --theme.primaryColor "#FF4B4B"
