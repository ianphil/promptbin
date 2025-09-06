# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PromptBin is a local-first prompt management and sharing tool with dual-mode operation:
- **MCP-Managed Mode**: MCP server (`mcp_server.py`) auto-launches Flask web interface
- **Standalone Mode**: Independent Flask app via `python app.py`

## Development Commands

Currently a minimal project with placeholder implementation. Development will require:

```bash
# Project is managed with uv package manager
uv install

# Run standalone web interface (when implemented)
python app.py

# Current main entry point
python main.py
```

## Architecture Overview

### Core Components
- **Flask Web App** (`app.py`): HTMX-powered interface on localhost:5000
- **MCP Server** (`mcp_server.py`): Model Context Protocol integration with auto-lifecycle management
- **File-Based Storage**: JSON files in `prompts/{category}/{prompt_id}.json`
- **Microsoft Dev Tunnels**: Secure sharing with automatic security protections

### Data Organization
```
prompts/
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

### Development Phases (per ai_docs/prompts.md)
1. **Core Local Functionality**: File storage, Flask app, HTMX templates
2. **MCP Integration**: Auto-lifecycle, prompt access protocol
3. **Sharing & Security**: Dev Tunnels, share tokens, rate limiting
4. **Polish & Enhancement**: Advanced highlighting, analytics

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

This project is in very early stages - currently only has a basic `main.py` placeholder. The comprehensive PRD and development prompts in `ai_docs/` define the full vision. Implementation should follow the 16-prompt sequence in `ai_docs/prompts.md` for systematic development.

Key architectural decisions are already documented - focus on implementing the planned dual-mode operation and file-based storage system as the foundation.