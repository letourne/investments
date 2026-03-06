#!/bin/bash
# Install Retirement Dashboard as systemd service
# Reads venv path from .venv_path file

echo "========================================"
echo "Installing Dashboard as System Service"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run with sudo"
    echo "Usage: sudo ./install_service.sh"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
if [ "$ACTUAL_USER" = "root" ]; then
    echo "❌ Cannot determine non-root user"
    exit 1
fi

# Get the working directory
WORKING_DIR="/home/pi/python/invest"

if [ ! -d "$WORKING_DIR" ]; then
    echo "❌ Working directory not found: $WORKING_DIR"
    exit 1
fi

echo "Installing service for user: $ACTUAL_USER"
echo "Working directory: $WORKING_DIR"
echo ""

# Check if .venv_path exists
if [ ! -f "$WORKING_DIR/.venv_path" ]; then
    echo "❌ .venv_path file not found in $WORKING_DIR"
    exit 1
fi

# Read venv path
VENV_PATH=$(cat "$WORKING_DIR/.venv_path" | tr -d '\n\r')

echo "Virtual environment: $VENV_PATH"

# Verify venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    exit 1
fi

echo "✓ Virtual environment found"
echo ""

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/retirement-dashboard.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Retirement Planning Dashboard
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$VENV_PATH/bin/python -m streamlit run $WORKING_DIR/retirement_dashboard_enhanced.py --server.address=0.0.0.0 --server.port=8502 --server.headless=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created: $SERVICE_FILE"

# Reload systemd
systemctl daemon-reload
echo "✓ Systemd reloaded"

# Enable service (auto-start on boot)
systemctl enable retirement-dashboard.service
echo "✓ Service enabled (will start on boot)"

# Start service now
systemctl start retirement-dashboard.service
echo "✓ Service started"

# Wait a moment
sleep 2

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "✅ Service Installation Complete!"
echo "========================================"
echo ""
echo "Service Commands:"
echo "  Start:   sudo systemctl start retirement-dashboard"
echo "  Stop:    sudo systemctl stop retirement-dashboard"
echo "  Restart: sudo systemctl restart retirement-dashboard"
echo "  Status:  sudo systemctl status retirement-dashboard"
echo "  Logs:    sudo journalctl -u retirement-dashboard -f"
echo ""
echo "Access Dashboard:"
echo "  Local:   http://localhost:8502"
echo "  Network: http://$IP_ADDR:8502"
echo ""
echo "The dashboard will now:"
echo "  • Start automatically on system boot"
echo "  • Restart automatically if it crashes"
echo "  • Run in the background (no terminal needed)"
echo ""
