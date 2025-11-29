# AI CLI 🤖

A modern, beautiful terminal-based LLM interface with file system access, powered by OpenRouter and Grok.

## Features ✨

- 🎨 **Beautiful UI** - Rich markdown rendering with syntax highlighting
- 📁 **File System Access** - Read and write files in your current directory
- 💬 **Interactive Chat** - Persistent conversation history
- ⚡ **Streaming Responses** - Real-time AI responses
- 🎯 **One-shot Mode** - Quick queries without entering interactive mode
- 🔒 **Secure** - API key stored locally in your config

## Installation 🚀

### Prerequisites

- Python 3.8 or higher
- pip
- OpenRouter API key ([Get one here](https://openrouter.ai/keys))

### Linux/macOS Quick Install

```bash
# Clone or download this repository
# Then run:
chmod +x install.sh
./install.sh
```

### Windows Installation

#### Using Command Prompt (CMD)
```cmd
install.bat
```

#### Using PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Manual Installation (All Platforms)

```bash
# Install dependencies
pip install -r requirements.txt

# Linux/macOS: Make executable and create symlink (optional)
chmod +x ai_cli.py
mkdir -p ~/.local/bin
ln -s $(pwd)/ai_cli.py ~/.local/bin/ai

# Add to PATH if not already (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

## Setup 🔧

1. Get your API key from [OpenRouter](https://openrouter.ai/keys)

2. Configure the CLI:
```bash
ai --setup
```

Or set environment variable:
```bash
export OPENROUTER_API_KEY='your-api-key-here'
```

## Usage 💡

### Interactive Mode

Start a conversation:
```bash
ai
```

Commands in interactive mode:
- `/clear` - Clear conversation history
- `/exit` or `/quit` - Exit the program
- `/read <file>` - Read and display a file
- `/write <file>` - Write next message to a file

### One-shot Mode

Quick queries:
```bash
ai "What is the capital of France?"
ai "Explain how async/await works in Python"
ai "Read the README.md file and summarize it"
```

### Examples

```bash
# Ask about files in current directory
ai "What Python files are in this directory?"

# Get code help
ai "Write a Python function to calculate fibonacci numbers"

# Analyze code
ai "Review the code in main.py and suggest improvements"

# File operations
ai "Read config.json and explain what it does"
```

## Configuration 📝

Config file location:
- Linux/macOS: `~/.config/ai-cli/config.json`
- Windows: `%APPDATA%\ai-cli\config.json`

You can manually edit this file to change settings:
```json
{
  "api_key": -api-key",
  "model": "x-ai/grok-4.1-fast:free"
}
```

## Models 🤖

Default model: `x-ai/grok-4.1-fast:free`

To use a different model:
```bash
ai --model "anthropic/claude-3-opus" "Your prompt here"
```

Available models on OpenRouter:
- `x-ai/grok-4.1-fast:free` (default - free tier)
- `openai/gpt-5.1-codex-mini`
- `google/gemini-2.5-flash`
- `google/gemini-2.0-flash-001`
- `google/gemini-2.5-flash-lite`
- And many more at [OpenRouter](https://openrouter.ai/models)

## Troubleshooting 🔧

### Command not found: ai

Make sure `~/.local/bin` is in your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### API Key Issues

- Verify your API key at [OpenRouter Keys](https://openrouter.ai/keys)
- Re-run setup: `ai --setup`
- Or set environment variable: `export OPENROUTER_API_KEY='your-key'`

### Module not found errors

Reinstall dependencies:
```bash
pip3 install --user -r requirements.txt
```

## License 📄

MIT License - Feel free to use and modify!

## Contributing 🤝

Contributions are welcome! Feel free to open issues or submit pull requests.
