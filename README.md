# PromptBin

## Overview

PromptBin is a local-first prompt management and sharing tool designed for AI prompt engineers and teams. It combines a web interface for prompt creation/management with MCP (Model Context Protocol) server integration for direct AI tool access, plus secure sharing capabilities via Microsoft Dev Tunnels.

Key features:
- **Local-first**: Your prompts stay private by default, stored locally
- **AI-integrated**: Direct access from Claude and other AI tools via MCP
- **Secure sharing**: Share specific prompts via temporary tunnels with automatic security protections
- **Developer-friendly**: File-based storage, no database setup required

## How to Run (Current State)

1. Install dependencies:
   ```bash
   uv install
   ```

2. Run the Flask web application:
   ```bash
   python app.py
   ```

3. Open your browser to `http://localhost:5000`

The application currently provides the basic web interface structure with HTMX integration. File-based storage and prompt management features are still in development.