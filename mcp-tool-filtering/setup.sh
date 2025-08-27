#!/bin/bash

echo "Setting up Redis MCP Latency Reduction Demo..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8+ first."
    echo "       Visit: https://python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "ERROR: Python 3.8+ required. Current version: Python $PYTHON_VERSION"
    echo "       Please upgrade Python"
    exit 1
fi

echo "OK: Python $PYTHON_VERSION found"

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo ""
    echo "ERROR: config.py not found"
    echo "       Please copy config.py.example to config.py and update with your credentials:"
    echo "       cp config.py.example config.py"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "OK: Dependencies installed"

# Configuration check
echo ""
echo "Checking configuration..."

# Extract Redis config from config.py using Python
REDIS_HOST=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['host'])" 2>/dev/null)
REDIS_PORT=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['port'])" 2>/dev/null)
REDIS_PWD=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['password'])" 2>/dev/null)
DEMO_PORT=$(python3 -c "from config import DEMO_CONFIG; print(DEMO_CONFIG['port'])" 2>/dev/null)

echo "Configuration loaded from config.py"

# Test Redis connection (optional)
echo ""
echo "Testing Redis connection..."

if [ -z "$REDIS_HOST" ] || [ "$REDIS_HOST" == "STUB_VALUE" ]; then
    echo "WARNING: Redis host not configured - demo will run in mock mode"
elif command -v redis-cli &> /dev/null; then
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PWD ping &> /dev/null 2>&1; then
        echo "OK: Redis connection successful"
    else
        echo "WARNING: Redis not accessible - demo will run in mock mode"
    fi
else
    echo "INFO: redis-cli not found - skipping Redis test"
    echo "      Demo will detect Redis availability automatically"
fi

echo ""
echo "Setup complete!"
echo "Starting demo server..."
echo ""

# Start the application
python3 app.py