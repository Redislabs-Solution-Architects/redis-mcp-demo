#!/bin/bash

# Quick Python version check before setup

echo "Checking Python version..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found"
    echo ""
    echo "Install Python 3.10+ from https://python.org/"
    exit 1
fi

VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

echo "Found: Python $VERSION"
echo ""

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "[ERROR] Python version too old"
    echo ""
    echo "Your version: $VERSION"
    echo "Recommended: 3.10-3.13"
    echo ""
    echo "Why: transformers library requires Python 3.10+"
    echo ""
    echo "Download: https://python.org/"
    exit 1
elif [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 14 ]; then
    echo "[ERROR] Python version too new"
    echo ""
    echo "Your version: $VERSION"
    echo "Recommended: 3.10-3.13"
    echo ""
    echo "Python 3.14+ has known issues:"
    echo "  - numpy/torch wheels not available"
    echo "  - Build from source fails"
    echo ""
    echo "Download Python 3.13 from https://python.org/"
    exit 1
else
    echo "[OK] Python version compatible"
    echo ""
    echo "Version: $VERSION"
    echo ""
    echo "You can proceed with setup:"
    echo "  ./setup.sh"
fi
