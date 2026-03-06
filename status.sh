#!/bin/bash
# Check status of Retirement Dashboard
# Includes port verification

PID_FILE=".retirement.pid"
LOG_FILE="retirement.log"
PORT=8502

echo "========================================"
echo "Retirement Dashboard - Status"
echo "========================================"
echo ""

# Function to check if port is in use
check_port() {
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":$PORT "
    elif command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep ":$PORT "
    else
        lsof -i :$PORT 2>/dev/null
    fi
}

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: ❌ Not running (no PID file)"
    echo ""
    
    # Double-check for orphaned processes
    PIDS=$(pgrep -f "streamlit run retirement_dashboard_enhanced.py")
    if [ -n "$PIDS" ]; then
        echo "⚠️  WARNING: Found orphaned process(es): $PIDS"
        echo "   These processes are running but not tracked"
        echo "   Run ./stop.sh to clean up"
        echo ""
    fi
    
    # Check if port is in use
    PORT_CHECK=$(check_port)
    if [ -n "$PORT_CHECK" ]; then
        echo "⚠️  WARNING: Port $PORT is in use:"
        echo "$PORT_CHECK"
        echo ""
        echo "Something else may be using this port"
        echo "Run ./stop.sh to attempt cleanup"
    else
        echo "Port $PORT: ✅ Available"
    fi
    
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p $PID > /dev/null 2>&1; then
    echo "Status: ✅ Running"
    echo "PID:    $PID"
    
    # Get process info
    echo ""
    echo "Process Details:"
    ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd | tail -n +2
    
    # Check port status
    echo ""
    echo "Port Status:"
    PORT_CHECK=$(check_port)
    if [ -n "$PORT_CHECK" ]; then
        echo "  Port $PORT: ✅ In use by this process"
        echo "  $PORT_CHECK"
    else
        echo "  Port $PORT: ⚠️  Not found (process may be starting)"
    fi
    
    # Get IP address
    IP_ADDR=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "Access URLs:"
    echo "  Local:   http://localhost:$PORT"
    echo "  Network: http://$IP_ADDR:$PORT"
    
    # Check if log file exists and show last few lines
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "Recent log entries (last 5 lines):"
        echo "-----------------------------------"
        tail -n 5 "$LOG_FILE"
        echo ""
        echo "View full log: tail -f $LOG_FILE"
    fi
    
    # Health check
    echo ""
    echo "Health Check:"
    if curl -s http://localhost:$PORT/_stcore/health > /dev/null 2>&1; then
        echo "  ✅ Dashboard is responding"
    else
        echo "  ⚠️  Dashboard may be starting or unresponsive"
    fi
else
    echo "Status: ⚠️  Stale PID file"
    echo "PID:    $PID (not running)"
    
    # Check if port is in use by something else
    echo ""
    PORT_CHECK=$(check_port)
    if [ -n "$PORT_CHECK" ]; then
        echo "⚠️  Port $PORT is in use by another process:"
        echo "$PORT_CHECK"
    else
        echo "Port $PORT: ✅ Available"
    fi
    
    echo ""
    echo "Run ./stop.sh to clean up, then ./start.sh to restart"
fi

echo ""
