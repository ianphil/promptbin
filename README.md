# PromptBin - MCP Server Example

**The easiest way to run a Model Context Protocol (MCP) server with full prompt management.**

## Quick Start

```bash
# Install from PyPI
uv add promptbin

# Run PromptBin (MCP server + web interface)
uv run promptbin
```

That's it! PromptBin is now running with both MCP server and web interface at `http://localhost:5001`.

## Add to AI Tools

### Claude Desktop (Mac/Windows)
Open Settings → Developer → Edit Config and add:

```json
{
  "mcpServers": {
    "promptbin": {
      "command": "promptbin"
    }
  }
}
```

### ChatGPT Desktop (Mac/Windows)
- Open Settings → Developer → Model Context Protocol
- Click "Add Server"
- Name: `promptbin`
- Command: `promptbin`

*Note: These configs assume global installation with `pip install promptbin`. For development, use `uv run promptbin`.*

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
