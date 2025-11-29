#!/bin/bash
# Installation script for AI CLI

set -e

echo "🚀 Installing AI CLI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Make the script executable
chmod +x ai_cli.py

# Create symlink in user's local bin
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

# Get the absolute path of the script
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/ai_cli.py"

# Create symlink
ln -sf "$SCRIPT_PATH" "$LOCAL_BIN/ai"

echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure $LOCAL_BIN is in your PATH"
echo "   Add this to your ~/.bashrc or ~/.zshrc:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "2. Reload your shell or run: source ~/.bashrc"
echo ""
echo "3. Set up your OpenRouter API key:"
echo "   ai --setup"
echo ""
echo "4. Start using AI CLI:"
echo "   ai                    # Interactive mode"
echo "   ai \"your prompt\"      # One-shot mode"
echo ""
echo "Get your API key at: https://openrouter.ai/keys"
