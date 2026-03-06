#!/bin/bash
# Stop Retirement Dashboard
# Verifies port is closed and no PIDs remain

echo "========================================"
echo "Stopping Retirement Dashboard"
echo "========================================"
echo ""

PID_FILE=".retirement.pid"
PORT=8502

# Function to check if port is in use
check_port() {
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":$PORT " | grep -v grep
    elif command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep ":$PORT " | grep -v grep
    else
        lsof -i :$PORT 2>/dev/null
    fi
}

# Function to find all related processes
find_processes() {
    pgrep -f "streamlit run retirement_dashboard_enhanced.py" 2>/dev/null
}

# Step 1: Check PID file
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "Found PID file: $PID"
    
    # Check if process is running
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping process $PID..."
        kill $PID
        sleep 1
        
        # Check if it stopped
        if ps -p $PID > /dev/null 2>&1; then
            echo "Process still running, forcing..."
            kill -9 $PID
            sleep 1
        fi
    else
        echo "Process $PID not running (stale PID file)"
    fi
    
    # Remove PID file
    rm -f "$PID_FILE"
    echo "✓ PID file removed"
else
    echo "No PID file found"
fi

echo ""

# Step 2: Look for any orphaned processes
echo "Checking for orphaned processes..."
ORPHANED=$(find_processes)

if [ -n "$ORPHANED" ]; then
    echo "⚠️  Found orphaned process(es): $ORPHANED"
    
    for pid in $ORPHANED; do
        echo "  Killing process $pid..."
        kill $pid 2>/dev/null
        sleep 0.5
        
        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
    done
    echo "✓ Orphaned processes cleaned up"
else
    echo "✓ No orphaned processes found"
fi

echo ""

# Step 3: Verify port is closed
echo "Verifying port $PORT is closed..."
sleep 1

PORT_CHECK=$(check_port)

if [ -n "$PORT_CHECK" ]; then
    echo "⚠️  Port $PORT is still in use:"
    echo "$PORT_CHECK"
    echo ""
    echo "Attempting to kill process using port $PORT..."
    
    # Extract PID from port check and kill it
    if command -v fuser &> /dev/null; then
        fuser -k $PORT/tcp 2>/dev/null
        sleep 1
    fi
    
    # Check again
    PORT_CHECK=$(check_port)
    if [ -n "$PORT_CHECK" ]; then
        echo "❌ Failed to close port $PORT"
        echo "Manual intervention may be required"
        exit 1
    else
        echo "✓ Port $PORT is now closed"
    fi
else
    echo "✓ Port $PORT is closed"
fi

echo ""

# Step 4: Final verification
echo "Final verification..."
REMAINING=$(find_processes)

if [ -n "$REMAINING" ]; then
    echo "❌ Warning: Some processes still running: $REMAINING"
    exit 1
fi

PORT_CHECK=$(check_port)
if [ -n "$PORT_CHECK" ]; then
    echo "❌ Warning: Port $PORT still in use"
    exit 1
fi

echo "✅ Dashboard stopped successfully"
echo "   - All processes terminated"
echo "   - Port $PORT is free"
echo "   - PID file removed"
echo ""
echo "Dashboard shut down complete and verified."
