#!/bin/bash
# BusyTag Demo Launcher for Mac/Linux

echo "🏷️  Starting BusyTag Demo Application..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed!"
    echo ""
    echo "Please install it with:"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Or if using uv:"
    echo "  uv pip install -r requirements.txt"
    exit 1
fi

# Check if busytag library is importable
python3 -c "import sys; sys.path.insert(0, '..'); import busytag" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: BusyTag library might not be installed properly"
    echo ""
fi

echo "🚀 Launching demo at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch streamlit
streamlit run app.py \
    --browser.gatherUsageStats false \
    --server.headless false \
    --theme.base light \
    --theme.primaryColor "#FF4B4B"
