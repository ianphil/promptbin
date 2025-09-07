# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PromptBin is the easiest way to run a Model Context Protocol (MCP) server with full prompt management capabilities. It's designed as a reference implementation and example for MCP server integration.

**Primary use case**: `uv add promptbin && uv run promptbin-mcp`

**Modes**:
- **MCP Server Mode** (primary): Full MCP protocol + auto-launching web interface
- **Standalone Mode** (secondary): Web interface only

## Development Commands

**For PyPI distribution (recommended)**:
```bash
# Install from PyPI
uv add promptbin

# Run MCP server (primary use case)
uv run promptbin-mcp

# Run standalone web interface
uv run promptbin

# Setup verification
uv run promptbin-setup

# Install Dev Tunnels CLI
uv run promptbin-install-tunnel
```

**For development**:
```bash
# Clone and develop
git clone https://github.com/ianphil/promptbin
cd promptbin
uv sync
uv run promptbin-mcp
```

## Architecture Overview

### Core Components
- **Flask Web App** (`app.py`): HTMX-powered interface on localhost:5000
- **MCP Server** (`mcp_server.py`): Model Context Protocol integration with auto-lifecycle management
- **File-Based Storage**: JSON files in `~/promptbin-data/{category}/{prompt_id}.json`
- **Microsoft Dev Tunnels**: Secure sharing with automatic security protections

### Data Organization
```
~/promptbin-data/
├── coding/     # Development-related prompts
├── writing/    # Content creation prompts  
└── analysis/   # Data analysis prompts
```

### Key Design Principles
- **Local-First**: All data stored locally by default
- **Zero Database**: File-based storage only
- **HTMX Integration**: No full page reloads, dynamic interactions
- **Security by Design**: Rate limiting (5 attempts per IP kills tunnel)
- **Template Variables**: Support for `{{variable}}` syntax with special highlighting

### Planned Technology Stack
- Backend: Python Flask with HTMX
- Frontend: HTML templates, highlight.js for syntax highlighting
- Storage: File-based JSON (no database)
- Sharing: Microsoft Dev Tunnels for external access
- MCP: Separate server component for AI tool integration

### Development Phases (Completed)
1. ✅ **Core Local Functionality**: File storage, Flask app, HTMX templates
2. ✅ **MCP Integration**: Auto-lifecycle, prompt access protocol
3. ✅ **Sharing & Security**: Dev Tunnels, share tokens, rate limiting
4. 🔄 **Polish & Enhancement**: Advanced highlighting, analytics (in progress)

### Security Architecture
- Private by default (localhost:5000)
- Explicit sharing via `/share/<token>/<prompt_id>` URLs only
- Rate limiting with automatic tunnel shutdown
- Origin validation prevents unauthorized tunnel access
- Cryptographically secure share tokens (ephemeral, reset on restart)

### MCP Protocol Integration
- AI tools access via `mcp://promptbin/get-prompt/prompt-name`
- Auto-start/stop web interface with MCP server lifecycle
- Health checks and process management
- Graceful shutdown with no orphaned processes

## Implementation Notes

Project is fully implemented with comprehensive features:

### Current Implementation Status
- ✅ **Dual-mode operation**: Both standalone and MCP-managed modes working
- ✅ **File-based storage**: JSON prompts organized by category
- ✅ **HTMX interface**: Dynamic UI without full page reloads
- ✅ **Dev Tunnels integration**: Secure public sharing with rate limiting
- ✅ **MCP server**: Full protocol implementation with AI tool access
- ✅ **Documentation & Setup**: Comprehensive guides and automation scripts

### Key Components
- `app.py`: Complete Flask web application with all routes and features
- `mcp_server.py`: Full MCP server implementation with subprocess management
- `prompt_manager.py`: File-based storage with search, categories, and metadata
- `share_manager.py`: Secure sharing with ephemeral tokens
- `tunnel_manager.py`: Microsoft Dev Tunnels integration with rate limiting
- `setup_checker.py`: System validation and diagnostic tool
- `scripts/install_devtunnel.py`: Cross-platform installer automation
- `TUNNELS.md`: Comprehensive technical documentation

### Environment Configuration
Supports extensive configuration via environment variables:
```bash
# Tunnel control
DEVTUNNEL_ENABLED=true
DEVTUNNEL_AUTO_START=false
DEVTUNNEL_RATE_LIMIT=5
DEVTUNNEL_RATE_WINDOW=30
DEVTUNNEL_LOG_LEVEL=info

# MCP server
PROMPTBIN_PORT=5000
PROMPTBIN_HOST=127.0.0.1
PROMPTBIN_DATA_DIR=~/promptbin-data
PROMPTBIN_LOG_LEVEL=INFO
```