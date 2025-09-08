# PromptBin - MCP Server Example

**The easiest way to run a Model Context Protocol (MCP) server with full prompt management.**

<img width="1200" height="296" alt="image" src="https://github.com/user-attachments/assets/f4609b53-bac7-4b58-871a-fee1b0f300ce" />


## Setup

### 1. Install and Configure

```bash
# Install PromptBin
pip install promptbin

# Install Dev Tunnels CLI (optional, for public sharing)
promptbin-install-tunnel

# Authenticate with Dev Tunnels (optional, one-time setup)
devtunnel user login -g

# Verify setup
promptbin-setup
```

### 2. Add to Your AI Client

**Claude Desktop** - Add to Settings → Developer → Edit Config:
```json
{
  "mcpServers": {
    "promptbin": {
      "type": "stdio",
      "command": "promptbin"
    }
  }
}
```

### 3. Start Using

That's it! PromptBin is now running:
- **Web UI**: `http://localhost:5001` - Manage and create prompts
- **MCP Server**: Ready for AI tool connections

## Key Features
- **🚀 Easy setup**: One command to get started
- **🔗 MCP integration**: Full Model Context Protocol support
- **🌐 Web interface**: Auto-launching prompt management UI
- **🔒 Secure sharing**: Share prompts via Dev Tunnels with rate limiting
- **📁 Local-first**: Your data stays private, stored locally
- **⚙️ Production-ready**: Comprehensive logging and error handling

## Usage Options

```bash
# Default: Run both MCP server and web interface
promptbin

# Run only MCP server (for AI tools)
promptbin --mcp

# Run only web interface (standalone)
promptbin --web

# Custom port and options
promptbin --port 8080 --data-dir ~/my-prompts
```

### Development Mode
For development or customization:
```bash
git clone https://github.com/ianphil/promptbin
cd promptbin
uv sync
uv run promptbin
```

## What You Get

- ✅ **Complete MCP server** - Full Model Context Protocol implementation
- ✅ **Auto-launching web UI** - Prompt management interface at localhost:5000
- ✅ **AI tool integration** - Works with Claude Desktop, ChatGPT Desktop
- ✅ **Secure sharing** - Share prompts publicly via Dev Tunnels
- ✅ **File-based storage** - No database required, organized by category
- ✅ **Cross-platform** - Windows, macOS, Linux support
- ✅ **Production-ready** - Rate limiting, logging, graceful shutdown

## Advanced Features

### Secure Public Sharing (Optional)
PromptBin includes Microsoft Dev Tunnels integration for sharing prompts publicly:

```bash
# Install Dev Tunnels CLI
uv run promptbin-install-tunnel

# Authenticate (one-time setup)
devtunnel user login -g

# Start PromptBin, then click "Start Tunnel" in the footer
```

Now your shared prompts get public URLs that work from anywhere. Includes automatic rate limiting and security protections.

For detailed setup instructions, see [TUNNELS.md](TUNNELS.md).

### System Validation
```bash
# Check if your system is ready
uv run promptbin-setup
```

## Add MCP Server to ChatGPT & Claude (Desktop)

Prereq: install deps first (`uv sync`). The apps will launch the MCP server themselves.

ChatGPT Desktop (Mac/Windows):
- Open Settings → Developer → Model Context Protocol.
- Click “Add Server”.
- Name: PromptBin
- Command: `uv`
- Args: `run python src/promptbin/mcp/server.py`
- Working directory: path to this repo.

Claude Desktop (Mac/Windows):
- Open Settings → Developer → Edit Config

```json
"PromptBin": {
            "command": "/Users/ianphil/.local/bin/uv",
            "args": [
                "run",
                "/Users/ianphil/src/promptbin/.venv/bin/python",
                "/Users/ianphil/src/promptbin/src/promptbin/mcp/server.py"
            ],
            "workingDirectory": "/Users/ianphil/src/promptbin"
        }
```

Notes:
- After adding, you can list/search prompts via the PromptBin MCP tools. The MCP server also starts the local web UI on `http://127.0.0.1:<port>`.
- If `uv` is not on PATH, replace `uv` with the full path or use your Python venv: `python src/promptbin/mcp/server.py`.
