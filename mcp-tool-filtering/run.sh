#!/bin/bash

# Simple script to run the demo after initial setup

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Redis MCP Tool Filtering Demo...${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo -e "${RED}[ERROR]${NC} config.py not found"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}[INFO]${NC} Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source "venv/Scripts/activate"
else
    source "venv/bin/activate"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to activate virtual environment"
    exit 1
fi

# Verify Python version in venv
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}[ERROR]${NC} Python 3.10+ required (found: Python $PYTHON_VERSION)"
    echo ""
    echo "Your virtual environment was created with Python $PYTHON_VERSION"
    echo "You need Python 3.10-3.13 for this demo."
    echo ""
    echo "Fix this by:"
    echo "  1. Install Python 3.10-3.13 from https://python.org/"
    echo "  2. Remove the old venv: rm -rf venv"
    echo "  3. Run setup again: ./setup.sh"
    exit 1
fi

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    echo -e "${YELLOW}[WARN]${NC} Python $PYTHON_VERSION may have compatibility issues"
    echo "Recommended: Python 3.10-3.13"
    echo ""
fi

# Get port from config
DEMO_PORT=$(python3 -c "from config import DEMO_CONFIG; print(DEMO_CONFIG['port'])" 2>/dev/null)

echo -e "${GREEN}[OK]${NC} Environment ready"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "  Server will start on port ${DEMO_PORT}"
echo -e "  Visit: http://localhost:${DEMO_PORT}"
echo -e "  Press Ctrl+C to stop"
echo -e "${BLUE}========================================${NC}"
echo ""

# Start the application
python3 app.py
