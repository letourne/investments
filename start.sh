#!/bin/bash
# Start Retirement Dashboard
# Reads venv path from .venv_path file

echo "========================================"
echo "Starting Retirement Dashboard"
echo "========================================"
echo ""

# Check if .venv_path exists
if [ ! -f ".venv_path" ]; then
    echo "❌ .venv_path file not found!"
    echo "Please create .venv_path with your venv path"
    echo "Example: echo '/opt/venvs/pi_projects' > .venv_path"
    exit 1
fi

# Read venv path from file
VENV_PATH=$(cat .venv_path | tr -d '\n\r')

echo "Using virtual environment: $VENV_PATH"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo "Run ./setup.sh first"
    exit 1
fi

# Check if dashboard file exists
if [ ! -f "retirement_dashboard_enhanced.py" ]; then
    echo "❌ retirement_dashboard_enhanced.py not found!"
    echo "Make sure you're in /home/pi/python/invest/"
    exit 1
fi

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo "Starting Streamlit server..."
echo ""
echo "═══════════════════════════════════════"
echo "Dashboard Access URLs:"
echo "═══════════════════════════════════════"
echo ""
echo "  Local (on this Pi):"
echo "    http://localhost:8502"
echo ""
echo "  Network (from any device):"
echo "    http://$IP_ADDR:8502"
echo ""
echo "═══════════════════════════════════════"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "────────────────────────────────────────"
echo ""

# PID file for process management
PID_FILE=".retirement.pid"
LOG_FILE="retirement.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "⚠️  Dashboard is already running (PID: $OLD_PID)"
        echo "To stop it first, run: ./stop.sh"
        exit 1
    else
        # Stale PID file, remove it
        rm "$PID_FILE"
    fi
fi

# Start streamlit in background
nohup python -m streamlit run retirement_dashboard_enhanced.py \
    --server.address=0.0.0.0 \
    --server.port=8502 \
    --server.headless=true \
    > "$LOG_FILE" 2>&1 &

# Save PID
STREAMLIT_PID=$!
echo $STREAMLIT_PID > "$PID_FILE"

# Wait a moment for startup
sleep 2

# Check if it's actually running
if ps -p $STREAMLIT_PID > /dev/null 2>&1; then
    echo "✅ Dashboard started successfully!"
    echo "   PID: $STREAMLIT_PID"
    echo ""
    echo "   View logs: tail -f $LOG_FILE"
    echo "   To stop:   ./stop.sh"
else
    echo "❌ Failed to start dashboard"
    echo "   Check logs: cat $LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi
