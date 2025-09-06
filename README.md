# PromptBin

## Overview

PromptBin is a local-first prompt management and sharing tool designed for AI prompt engineers and teams. It combines a web interface for prompt creation/management with MCP (Model Context Protocol) server integration for direct AI tool access, plus secure sharing capabilities via Microsoft Dev Tunnels.

Key features:
- **Local-first**: Your prompts stay private by default, stored locally
- **AI-integrated**: Direct access from Claude and other AI tools via MCP
- **Secure sharing**: Share specific prompts via temporary tunnels with automatic security protections
- **Developer-friendly**: File-based storage, no database setup required

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

- ✅ Full web interface with prompt management
- ✅ MCP server with protocol handlers for AI tool access
- ⏳ Flask subprocess integration (Phase 3)
- ⏳ Secure sharing via Dev Tunnels