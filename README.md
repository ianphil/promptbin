# PromptBin

## Overview

PromptBin is a local-first prompt management and sharing tool designed for AI prompt engineers and teams. It combines a web interface for prompt creation/management with MCP (Model Context Protocol) server integration for direct AI tool access, plus secure sharing capabilities via Microsoft Dev Tunnels.

Key features:
- **Local-first**: Your prompts stay private by default, stored locally
- **AI-integrated**: Direct access from Claude and other AI tools via MCP
- **Secure sharing**: Share specific prompts via temporary tunnels with automatic security protections
- **Developer-friendly**: File-based storage, no database setup required
- **Cross-platform**: Works on Linux, macOS, and Windows with automated setup
- **Production-ready**: Rate limiting, proper error handling, and comprehensive logging
- **Configurable**: Extensive environment variable support for all features

## How to Run

1. Install dependencies:
   ```bash
   uv sync
   ```

2. **Standalone mode** - Run just the web interface:
   ```bash
   uv run python app.py
   ```
   Open your browser to `http://localhost:5000`

3. **MCP mode** - Run MCP server (auto-launches web interface):
   ```bash
   uv run python mcp_server.py
   ```
   Provides MCP protocol access for AI tools + web interface

## Current Status

- ✅ **Full web interface** with prompt management, search, and categories
- ✅ **MCP server** with protocol handlers for AI tool access
- ✅ **Flask subprocess integration** with automatic lifecycle management
- ✅ **Secure sharing via Dev Tunnels** with rate limiting and automatic security
- ✅ **Cross-platform setup automation** with installer scripts and validation
- ✅ **Comprehensive documentation** including technical guides and troubleshooting
- ✅ **Environment variable configuration** for all major features
- ✅ **Production-ready** with proper error handling, logging, and cleanup

## Dev Tunnels Setup (Optional - For Public Sharing)

PromptBin includes integrated Microsoft Dev Tunnels support for secure public sharing of prompts. This is optional but enables sharing prompts with people outside your network.

### Prerequisites

- Microsoft account or GitHub account (for authentication)
- Internet connection for tunnel creation

### Installation

#### Automated Installation (All Platforms)
```bash
# Run the installer script
python scripts/install_devtunnel.py

# Or after installing PromptBin:
uv run promptbin-install-tunnel
```

#### Linux (Manual Method)
```bash
# Download and install directly
curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/

# Verify installation
devtunnel --version
```

#### macOS
```bash
# Option 1: Homebrew (recommended)
brew install --cask devtunnel

# Option 2: Direct download
curl -sL https://aka.ms/TunnelsCliDownload/osx-x64 -o devtunnel
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

#### Windows
```powershell
# Option 1: winget (recommended)
winget install Microsoft.devtunnel

# Option 2: PowerShell download
Invoke-WebRequest -Uri "https://aka.ms/TunnelsCliDownload/win-x64" -OutFile "devtunnel.exe"
# Move to a directory in your PATH
```

### Authentication Setup

After installation, authenticate with your Microsoft or GitHub account:

```bash
# Option 1: Microsoft account
devtunnel user login

# Option 2: GitHub account (recommended)
devtunnel user login -g

# Verify authentication
devtunnel user show
```

### Using Tunnels in PromptBin

1. **Start the app**: `uv run python app.py`
2. **Start tunnel**: Click "Start Tunnel" in the footer
3. **Share prompts**: Share button will now generate public URLs
4. **Stop tunnel**: Click "Stop Tunnel" when done

### Security Features

- **Rate limiting**: 5 tunnel attempts per IP per 30 minutes
- **Automatic cleanup**: Tunnels stop when app shuts down
- **Anonymous access**: Share links work without authentication
- **Auto-shutdown**: Tunnels stop automatically on abuse

### Setup Verification

```bash
# Check if your system is ready for Dev Tunnels
python setup_checker.py

# Or after installing PromptBin:
uv run promptbin-setup
```

### Troubleshooting

**CLI not found**: Ensure `devtunnel` is in your system PATH
**Authentication failed**: Run `devtunnel user login -g` again
**Tunnel won't start**: Check authentication with `devtunnel user show`
**Rate limited**: Wait 30 minutes or restart the app

For detailed troubleshooting, see [TUNNELS.md](TUNNELS.md).

## Add MCP Server to ChatGPT & Claude (Desktop)

Prereq: install deps first (`uv sync`). The apps will launch the MCP server themselves.

ChatGPT Desktop (Mac/Windows):
- Open Settings → Developer → Model Context Protocol.
- Click “Add Server”.
- Name: PromptBin
- Command: `uv`
- Args: `run python mcp_server.py`
- Working directory: path to this repo.

Claude Desktop (Mac/Windows):
- Open Settings → Developer → Edit Config

```json
"PromptBin": {
            "command": "/Users/ianphil/.local/bin/uv",
            "args": [
                "run",
                "/Users/ianphil/src/promptbin/.venv/bin/python",
                "/Users/ianphil/src/promptbin/mcp_server.py"
            ],
            "workingDirectory": "/Users/ianphil/src/promptbin"
        }
```

Notes:
- After adding, you can list/search prompts via the PromptBin MCP tools. The MCP server also starts the local web UI on `http://127.0.0.1:<port>`.
- If `uv` is not on PATH, replace `uv` with the full path or use your Python venv: `python mcp_server.py`.
