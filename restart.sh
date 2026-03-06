#!/bin/bash
# Restart Retirement Dashboard

echo "========================================"
echo "Restarting Retirement Dashboard"
echo "========================================"
echo ""

# Stop if running
if [ -f ".retirement.pid" ]; then
    echo "Stopping current instance..."
    ./stop.sh
    echo ""
    
    # Wait a moment
    sleep 2
fi

# Start
echo "Starting dashboard..."
./start.sh
