#!/bin/bash
# Raspberry Pi Setup - Uses .venv_path file
# Project location: /home/pi/python/invest/

echo "========================================"
echo "Retirement Dashboard - Setup"
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

echo "Reading virtual environment path from .venv_path"
echo "Virtual environment: $VENV_PATH"
echo ""

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    echo "Please check the path in .venv_path"
    exit 1
fi

echo "✓ Found virtual environment"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"
echo ""

# Check if streamlit is already installed
if python -c "import streamlit" &> /dev/null; then
    echo "✓ Streamlit is already installed"
    STREAMLIT_VERSION=$(python -c "import streamlit; print(streamlit.__version__)")
    echo "  Version: $STREAMLIT_VERSION"
else
    echo "Installing Streamlit..."
    pip install streamlit
fi

# Check other required packages
echo ""
echo "Checking required packages..."

for package in numpy pandas plotly; do
    if python -c "import $package" &> /dev/null; then
        echo "  ✓ $package installed"
    else
        echo "  Installing $package..."
        pip install $package
    fi
done

echo ""
echo "✓ All packages ready"
echo ""

# Create .streamlit directory and config
echo "Setting up Streamlit configuration..."
mkdir -p .streamlit

cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
address = "0.0.0.0"
port = 8502
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8502

[theme]
base = "dark"
primaryColor = "#40c4ff"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"

[client]
showErrorDetails = true
EOF

echo "✓ Configuration created"
echo ""

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Project location: /home/pi/python/invest/"
echo "Virtual environment: $VENV_PATH"
echo ""
echo "To start the dashboard:"
echo "  ./start.sh"
echo ""
echo "Access URLs:"
echo "  Local:   http://localhost:8502"
echo "  Network: http://$IP_ADDR:8502"
echo ""
echo "To install as auto-start service:"
echo "  sudo ./install_service.sh"
echo ""
