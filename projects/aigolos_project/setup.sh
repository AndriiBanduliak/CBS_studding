#!/bin/bash

# AIGolos - Setup Script
# Author: Andrii Banduliak
# This script sets up the project environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AIGolos Setup Script${NC}"
echo -e "${BLUE}  Author: Andrii Banduliak${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verify we're in the right directory (check for app directory)
if [ ! -d "app" ]; then
    print_warning "app/ directory not found. This might not be the project root."
    print_info "Current directory: $(pwd)"
    print_info "Creating basic project structure..."
    
    # Create basic structure
    mkdir -p app/api
    mkdir -p app/models
    mkdir -p app/services
    mkdir -p app/static
    mkdir -p app/templates
    mkdir -p app/utils
    mkdir -p config
    mkdir -p tests
    mkdir -p docker
    
    print_warning "Created basic directories. You may need to add project files manually."
fi

# Check Python version
print_info "Checking Python installation..."

# Try python3 first, then python
PYTHON_CMD=""
PIP_CMD=""
PYTHON_VERSION_OUT=""

# Check python3
if command -v python3 &> /dev/null 2>&1; then
    PYTHON_VERSION_OUT=$(python3 --version 2>&1) || PYTHON_VERSION_OUT=""
    # Filter out Microsoft Store messages
    if [[ -n "$PYTHON_VERSION_OUT" ]] && \
       [[ "$PYTHON_VERSION_OUT" != *"Microsoft Store"* ]] && \
       [[ "$PYTHON_VERSION_OUT" != *"not found"* ]] && \
       [[ "$PYTHON_VERSION_OUT" != *"Windows Store"* ]] && \
       [[ "$PYTHON_VERSION_OUT" =~ [0-9]+\.[0-9]+ ]]; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    fi
fi

# If python3 not found or failed, try python
if [[ -z "$PYTHON_CMD" ]]; then
    if command -v python &> /dev/null 2>&1; then
        PYTHON_VERSION_OUT=$(python --version 2>&1) || PYTHON_VERSION_OUT=""
        # Filter out Microsoft Store messages
        if [[ -n "$PYTHON_VERSION_OUT" ]] && \
           [[ "$PYTHON_VERSION_OUT" != *"Microsoft Store"* ]] && \
           [[ "$PYTHON_VERSION_OUT" != *"not found"* ]] && \
           [[ "$PYTHON_VERSION_OUT" != *"Windows Store"* ]] && \
           [[ "$PYTHON_VERSION_OUT" =~ [0-9]+\.[0-9]+ ]]; then
            PYTHON_CMD="python"
            PIP_CMD="pip"
        fi
    fi
fi


if [[ -z "$PYTHON_CMD" ]] || [[ -z "$PYTHON_VERSION_OUT" ]]; then
    print_error "Python not found! Please install Python 3.10 or higher."
    print_error ""
    print_error "Troubleshooting:"
    print_error "1. Make sure Python 3.10+ is installed from python.org"
    print_error "2. On Windows, disable Microsoft Store Python alias:"
    print_error "   Settings > Apps > Advanced app settings > App execution aliases"
    print_error "3. Add Python to PATH during installation"
    print_error "4. Verify: python --version or python3 --version"
    exit 1
fi

# Extract version number
PYTHON_VERSION=""
if [[ $PYTHON_VERSION_OUT =~ ([0-9]+\.[0-9]+\.[0-9]+) ]]; then
    PYTHON_VERSION=${BASH_REMATCH[1]}
elif [[ $PYTHON_VERSION_OUT =~ ([0-9]+\.[0-9]+) ]]; then
    PYTHON_VERSION=${BASH_REMATCH[1]}
fi

# Check if version is 3.10 or higher
if [[ -n "$PYTHON_VERSION" ]] && [[ $PYTHON_VERSION =~ ^([0-9]+)\.([0-9]+) ]]; then
    MAJOR=${BASH_REMATCH[1]}
    MINOR=${BASH_REMATCH[2]}
    
    if [[ $MAJOR -lt 3 ]] || ([[ $MAJOR -eq 3 ]] && [[ $MINOR -lt 10 ]]); then
        print_error "Python 3.10+ required. Found: Python $PYTHON_VERSION"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION found ($PYTHON_CMD)"
else
    print_warning "Could not parse Python version. Continuing anyway..."
    print_warning "Using: $PYTHON_CMD"
fi

# Check pip
print_info "Checking pip installation..."
if ! $PIP_CMD --version &> /dev/null 2>&1; then
    print_info "pip not found. Installing pip..."
    if ! $PYTHON_CMD -m ensurepip --upgrade 2>&1; then
        print_error "Failed to install pip"
        print_error "Try: $PYTHON_CMD -m ensurepip --upgrade manually"
        exit 1
    fi
fi
PIP_VERSION=$($PIP_CMD --version 2>&1 | head -n1)
print_success "pip found ($PIP_CMD)"

# Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv || {
        print_error "Failed to create virtual environment"
        exit 1
    }
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    VENV_PYTHON="venv/bin/python"
    VENV_PIP="venv/bin/pip"
elif [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
    VENV_PYTHON="venv/Scripts/python.exe"
    VENV_PIP="venv/Scripts/pip.exe"
else
    print_error "Could not find virtual environment activation script"
    exit 1
fi

# Use venv Python and pip
PYTHON_CMD="$VENV_PYTHON"
PIP_CMD="$VENV_PIP"

# Upgrade pip
print_info "Upgrading pip..."
$VENV_PYTHON -m pip install --upgrade pip --quiet 2>/dev/null || {
    print_warning "Failed to upgrade pip, continuing anyway..."
}

# Install Python dependencies
print_info "Installing Python dependencies..."

# Check requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found! Please create it before running setup."
    exit 1
fi

$VENV_PIP install -r requirements.txt || {
    print_error "Failed to install dependencies"
    exit 1
}
print_success "Python dependencies installed"

# Install faster-whisper (optional, can fail)
print_info "Attempting to install faster-whisper..."
if $VENV_PIP install faster-whisper --quiet 2>/dev/null; then
    print_success "faster-whisper installed"
else
    print_warning "faster-whisper installation failed. You can install it manually later: $VENV_PIP install faster-whisper"
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p models
mkdir -p temp_audio
mkdir -p config
print_success "Directories created"

# Check for .env file
print_info "Checking configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating default .env file..."
    cat > .env << 'EOF'
# ASR Settings
ASR_MODEL_NAME=large-v3
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8

# LLM Settings
LLM_BACKEND=ollama
LLM_MODEL_NAME=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
LLM_MAX_TOKENS=256
LLM_TEMPERATURE=0.7

# TTS Settings
TTS_VOICE_NAME=de_DE/thorsten/medium
TTS_MODEL_PATH=

# Application Settings
APP_HOST=127.0.0.1
APP_PORT=8000
DEBUG=false

# Session Settings
SESSION_TIMEOUT=3600
MAX_AUDIO_SIZE=10485760
EOF
    print_success ".env file created"
else
    print_success ".env file found"
fi

# Check for external dependencies
print_info "Checking external dependencies..."

# Check Ollama
if command -v ollama &> /dev/null; then
    if ollama list &> /dev/null; then
        print_success "Ollama is installed and running"
        echo ""
        print_info "Available Ollama models:"
        ollama list 2>/dev/null | grep -v "^NAME" | awk '{print "  - " $1}' || echo "  No models found"
    else
        print_warning "Ollama is installed but not running. Start it with: ollama serve"
    fi
else
    print_warning "Ollama not found. Install from: https://ollama.ai"
    print_warning "After installation, run: ollama pull qwen2.5:7b"
fi

# Check Piper TTS
if command -v piper &> /dev/null; then
    print_success "Piper TTS is installed"
else
    print_warning "Piper TTS not found. Install from: https://github.com/rhasspy/piper/releases"
    print_warning "Or use: pip install piper-tts"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Make sure Ollama is running:"
echo "   ollama serve"
echo ""
echo "2. Activate virtual environment:"
if [ -f "venv/bin/activate" ]; then
    echo "   source venv/bin/activate"
else
    echo "   source venv/Scripts/activate  # Windows Git Bash"
fi
echo ""
echo "3. Start the application:"
if [ -n "$VENV_PYTHON" ]; then
    echo "   $VENV_PYTHON -m uvicorn app.main:app --reload"
else
    echo "   uvicorn app.main:app --reload"
fi
echo ""
echo "4. Open in browser:"
echo "   http://localhost:8000"
echo ""
echo -e "${YELLOW}Optional dependencies:${NC}"
if [ -n "$VENV_PIP" ]; then
    echo "- Install faster-whisper: $VENV_PIP install faster-whisper"
else
    echo "- Install faster-whisper: $PIP_CMD install faster-whisper"
fi
echo "- Install Piper TTS: See https://github.com/rhasspy/piper"
echo "- Pull Ollama model: ollama pull qwen2.5:7b"
echo ""
echo -e "${BLUE}For more information, see README.md${NC}"

