#!/bin/bash

set -e  # Exit on error

# Color codes for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Redis MCP Tool Filtering Demo Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored output
print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if Python 3 is installed
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo ""
    echo "Install Python 3.10-3.13 from https://python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ required (found: Python $PYTHON_VERSION)"
    echo ""
    echo "The transformers library requires Python 3.10+ syntax."
    echo ""
    echo "Current version: $PYTHON_VERSION"
    echo "Recommended: 3.10-3.13"
    echo "Download: https://python.org/"
    exit 1
fi

# Warn if Python is 3.14+ (known issues with numpy)
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
    print_warning "Python $PYTHON_VERSION detected"
    echo ""
    echo "Python 3.14+ has known issues with numpy/torch wheels."
    echo "Recommended: Python 3.10-3.13"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 1
    fi
fi

print_success "Python $PYTHON_VERSION found"

# Check if config.py exists, if not create it from example
if [ ! -f "config.py" ]; then
    print_error "config.py not found"
    if [ -f "config.py.example" ]; then
        print_info "Creating config.py from template"
        cp config.py.example config.py
        echo ""
        print_warning "You must edit config.py and replace STUB_VALUE entries:"
        echo "  - _redis_endpoint: your Redis Cloud endpoint"
        echo "  - _redis_password: your Redis password"
        echo "  - OPENAI api_key: your OpenAI API key"
        echo ""
        print_error "Setup cannot continue with STUB_VALUE placeholders"
        echo "After updating config.py, run ./setup.sh again"
        exit 1
    else
        print_error "config.py.example not found"
        exit 1
    fi
fi

print_success "Configuration file found"

# Validate config.py doesn't contain STUB_VALUE
print_info "Validating configuration..."
if grep -q "STUB_VALUE" config.py; then
    print_error "config.py still contains STUB_VALUE placeholders"
    echo ""
    echo "Please edit config.py and replace all STUB_VALUE entries:"
    echo "  - _redis_endpoint: your Redis Cloud endpoint"
    echo "  - _redis_password: your Redis password"
    echo "  - OPENAI api_key: your OpenAI API key"
    echo ""
    echo "After updating config.py, run ./setup.sh again"
    exit 1
fi
print_success "Configuration validated"

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        echo ""
        echo "Try installing python3-venv:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-venv"
        echo "  macOS: Should work by default with Python 3.3+"
        exit 1
    fi
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source "$VENV_DIR/Scripts/activate"
else
    # Unix-like
    source "$VENV_DIR/bin/activate"
fi

if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

print_success "Virtual environment activated"

# Upgrade pip to avoid dependency resolution issues
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
echo ""
print_info "Installing dependencies (5-10 min, ~500MB download)"
echo ""

# Install dependencies with progress
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    echo ""
    echo "Common issues:"
    echo "  - Network connection problems"
    echo "  - Insufficient disk space"
    echo "  - Missing system dependencies"
    echo ""
    echo "Try running manually:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo ""
print_success "All dependencies installed successfully"

# Verify sentence-transformers installation
print_info "Verifying sentence-transformers installation..."
IMPORT_ERROR=$(python3 -c "from sentence_transformers import SentenceTransformer" 2>&1)
if [ $? -eq 0 ]; then
    print_success "sentence-transformers verified"
else
    print_error "sentence-transformers import failed"
    echo ""
    echo "Error details:"
    echo "$IMPORT_ERROR" | head -5
    echo ""
    if echo "$IMPORT_ERROR" | grep -q "unsupported operand type(s) for |"; then
        print_error "Python version incompatibility"
        echo ""
        echo "Current: Python $PYTHON_VERSION"
        echo "Required: Python 3.10-3.13"
        echo "Download: https://python.org/"
    else
        echo "Please ensure sentence-transformers is installed correctly."
    fi
    exit 1
fi

# Configuration validation
echo ""
print_info "Validating configuration..."

# Check if config has stub values
HAS_STUBS=$(python3 -c "
from config import REDIS_CONFIG, OPENAI_CONFIG
stub_count = 0
if 'STUB_VALUE' in str(REDIS_CONFIG.get('endpoint', '')): stub_count += 1
if 'STUB_VALUE' in str(OPENAI_CONFIG.get('api_key', '')): stub_count += 1
print(stub_count)
" 2>/dev/null)

if [ "$HAS_STUBS" != "0" ]; then
    print_warning "Configuration incomplete (STUB_VALUE found)"
    echo ""
    echo "Update config.py with actual credentials:"
    echo "  - Redis: endpoint, username, password"
    echo "  - OpenAI: api_key"
    echo ""
    echo "Demo will start but may run in limited mode"
    echo ""
fi

# Extract config for display
REDIS_ENDPOINT=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG.get('endpoint', REDIS_CONFIG.get('host', 'unknown')))" 2>/dev/null)
DEMO_PORT=$(python3 -c "from config import DEMO_CONFIG; print(DEMO_CONFIG['port'])" 2>/dev/null)

print_success "Configuration loaded"

# Test Redis connection (optional)
echo ""
print_info "Testing Redis connection..."

if [ -z "$REDIS_ENDPOINT" ] || [ "$REDIS_ENDPOINT" == "STUB_VALUE" ]; then
    print_warning "Redis not configured - demo will run in limited mode"
elif command -v redis-cli &> /dev/null; then
    REDIS_HOST=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['host'])" 2>/dev/null)
    REDIS_PORT=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['port'])" 2>/dev/null)
    REDIS_PWD=$(python3 -c "from config import REDIS_CONFIG; print(REDIS_CONFIG['password'])" 2>/dev/null)

    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PWD" ping &> /dev/null 2>&1; then
        print_success "Redis connection successful"
    else
        print_warning "Redis not accessible - demo will run in limited mode"
    fi
else
    print_info "redis-cli not installed - skipping connection test"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Starting server on port $DEMO_PORT"
echo "URL: http://localhost:$DEMO_PORT"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# Start the application
python3 app.py