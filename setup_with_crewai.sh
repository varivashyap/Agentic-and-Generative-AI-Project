#!/bin/bash

# Study Assistant Setup Script with CrewAI
# This script helps install dependencies in stages to avoid conflicts

set -e  # Exit on error

echo "🚀 Setting up Study Assistant with CrewAI integration"
echo "=================================================="

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

if [[ $(python3 -c "import sys; print(sys.version_info >= (3, 8))") == "False" ]]; then
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

echo "✅ Python version is compatible"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "🔧 Installing core dependencies..."
echo "This includes basic packages that are generally stable..."
pip install -r requirements-core.txt

if [ $? -eq 0 ]; then
    echo "✅ Core dependencies installed successfully"
else
    echo "❌ Failed to install core dependencies"
    echo "Please check the error messages above and resolve any issues"
    exit 1
fi

# Test core functionality
echo "🧪 Testing core functionality..."
if python -c "import pdfplumber, flask, pandas, numpy; print('Core imports successful')" 2>/dev/null; then
    echo "✅ Core modules import successfully"
else
    echo "❌ Core modules failed to import"
    exit 1
fi

# Install advanced dependencies
echo "🚀 Installing advanced dependencies (including CrewAI)..."
echo "This may take longer and could have compatibility issues..."

# Try installing advanced dependencies
if pip install -r requirements-advanced.txt; then
    echo "✅ Advanced dependencies installed successfully"
    CREWAI_AVAILABLE=true
else
    echo "⚠️  Some advanced dependencies failed to install"
    echo "You can still use the basic Study Assistant functionality"
    echo "CrewAI features may not be available"
    CREWAI_AVAILABLE=false
fi

# Test imports
echo "🧪 Testing imports..."

echo "Testing basic imports..."
if python -c "
import sys
sys.path.append('.')
from src.config import get_config
from src.ingestion import PDFIngestion
print('✅ Basic Study Assistant modules import successfully')
" 2>/dev/null; then
    echo "✅ Basic functionality available"
    BASIC_AVAILABLE=true
else
    echo "❌ Basic functionality failed - check dependencies"
    BASIC_AVAILABLE=false
fi

if [ "$CREWAI_AVAILABLE" = true ]; then
    echo "Testing CrewAI imports..."
    if python -c "
import crewai
import langchain
print('✅ CrewAI modules import successfully')
" 2>/dev/null; then
        echo "✅ CrewAI functionality available"
    else
        echo "⚠️  CrewAI imports failed despite installation"
        CREWAI_AVAILABLE=false
    fi
fi

# Test pipeline initialization
echo "🔧 Testing pipeline initialization..."
if python -c "
import sys
sys.path.append('.')
from src.pipeline import StudyAssistantPipeline
pipeline = StudyAssistantPipeline()
print('✅ Pipeline initialized successfully')
if hasattr(pipeline, 'crewai_orchestrator') and pipeline.crewai_orchestrator:
    print('✅ CrewAI orchestrator available')
else:
    print('⚠️  CrewAI orchestrator not available (using standard pipeline)')
" 2>/dev/null; then
    echo "✅ Pipeline test successful"
else
    echo "❌ Pipeline initialization failed"
    echo "Please check the logs above for specific errors"
fi

# Summary
echo ""
echo "📋 Setup Summary"
echo "================"
if [ "$BASIC_AVAILABLE" = true ]; then
    echo "✅ Basic Study Assistant: Available"
else
    echo "❌ Basic Study Assistant: Failed"
fi

if [ "$CREWAI_AVAILABLE" = true ]; then
    echo "✅ CrewAI Enhanced Features: Available" 
else
    echo "⚠️  CrewAI Enhanced Features: Not Available"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Test the CLI: python examples/crewai_cli.py --status"
echo "2. Try examples: python examples/crewai_examples.py"
echo "3. Start MCP server: python mcp_server/server.py"

if [ "$CREWAI_AVAILABLE" = false ]; then
    echo ""
    echo "⚠️  CrewAI Troubleshooting:"
    echo "- Check Python version (3.8+ required)"
    echo "- Try installing CrewAI separately: pip install crewai==0.70.1"
    echo "- Check for system-specific compatibility issues"
    echo "- You can still use all basic Study Assistant features"
fi

echo ""
echo "🔗 Documentation:"
echo "- Main README: README.md"
echo "- CrewAI Integration: CREWAI_INTEGRATION.md"
echo "- Configuration: config/config.yaml"

echo ""
echo "✅ Setup completed!"