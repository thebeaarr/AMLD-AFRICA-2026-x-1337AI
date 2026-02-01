#!/bin/bash

echo "🚀 AI Study Assistant - Chrome Extension Setup"
echo "=============================================="
echo ""

# Check if in correct directory
if [ ! -d "backend" ] || [ ! -d "extension" ]; then
    echo "❌ Error: Please run this script from the hackathon root directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Note: Using mock mode. Edit backend/.env to add API keys for production."
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   python main.py"
echo ""
echo "2. Install Chrome Extension:"
echo "   - Open Chrome and go to: chrome://extensions/"
echo "   - Enable 'Developer mode' (toggle top-right)"
echo "   - Click 'Load unpacked'"
echo "   - Select the 'extension' folder"
echo ""
echo "3. Configure extension:"
echo "   - Click extension icon"
echo "   - Verify API URL: http://localhost:8000"
echo "   - Click 'Save Settings'"
echo ""
echo "4. Try it out:"
echo "   - Go to any webpage"
echo "   - Highlight some text (>10 characters)"
echo "   - Click the 'Capture' button"
echo ""
echo "🎉 Happy hacking!"
