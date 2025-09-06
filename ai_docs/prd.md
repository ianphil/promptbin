# PromptBin - Product Requirements Document

## Overview
PromptBin is a local-first prompt management and sharing tool designed for AI prompt engineers and teams. It combines a web interface for prompt creation/management with MCP (Model Context Protocol) server integration for direct AI tool access, plus secure sharing capabilities via Microsoft Dev Tunnels.

## Core Value Proposition
- **Local-first**: Your prompts stay private by default, stored locally
- **AI-integrated**: Direct access from Claude and other AI tools via MCP
- **Secure sharing**: Share specific prompts via temporary tunnels with automatic security protections
- **Developer-friendly**: File-based storage, no database setup required

## Application Lifecycle Management

### Operational Modes

#### Mode 1: MCP-Managed (Primary Mode)
**Startup Sequence:**
1. MCP server (`mcp_server.py`) is loaded by AI tool (Claude, etc.)
2. MCP server automatically launches Flask web interface on `localhost:5000`
3. Both MCP protocol endpoints and web UI become available simultaneously
4. User can access prompt management via browser while AI tools access via MCP

**Shutdown Sequence:**
1. AI tool unloads MCP server
2. MCP server gracefully shuts down Flask web interface
3. All services stop cleanly, no orphaned processes

**Benefits:**
- Zero manual intervention required
- Web UI availability perfectly matches AI tool integration
- Automatic resource cleanup
- Seamless developer experience

#### Mode 2: Standalone Web Interface
**Startup:**
```bash
python app.py
```
- Flask app starts independently on `localhost:5000`
- No MCP server running
- Pure web-based prompt management
- Useful for prompt organization without AI tool integration

### Tunnel Lifecycle Within Sessions

#### Default State (Private)
- All URLs use `localhost:5000` format
- Prompts accessible only on local machine
- "Start Tunnel" button available in UI
- Copy URL buttons show local addresses

#### Tunnel Active State (Shareable)
**Activation:**
1. User clicks "Start Tunnel" button in web interface
2. Flask app spawns Microsoft Dev Tunnel process
3. UI updates to show tunnel status and public URL
4. Copy URL buttons automatically switch to tunnel format: `https://abc123.devtunnels.ms/share/token/prompt-id`

**Automatic Security:**
- Rate limiting monitors external access attempts
- 5 failed attempts from any IP triggers automatic tunnel shutdown
- UI shows security alerts and failed attempt counts
- User can manually restart tunnel after reviewing activity

**Manual Deactivation:**
- User clicks "Stop Tunnel" button
- Tunnel process terminates
- UI reverts to localhost URLs
- Sharing links become inactive

### State Persistence
- **Prompt data**: Persisted in local file system across all lifecycle events
- **Tunnel state**: Ephemeral, resets on application restart
- **Share tokens**: Generated per session, invalid after restart
- **MCP availability**: Dependent on parent AI tool lifecycle

### Error Handling & Recovery
- **MCP server crash**: Web interface auto-shuts down, no zombie processes
- **Web interface crash**: MCP server remains functional, web UI can be restarted
- **Tunnel failure**: Automatic fallback to local-only mode with user notification
- **File system issues**: Graceful degradation with clear error messaging

## Architecture

### Technology Stack
- **Backend**: Python Flask with HTMX for dynamic interactions
- **Frontend**: HTML templates with HTMX, highlight.js for syntax highlighting
- **Storage**: File-based system (no database required)
- **MCP Integration**: Separate Python MCP server component
- **Sharing**: Microsoft Dev Tunnels for secure external access

### File Structure
```
promptbin/
├── app.py                    # Flask web application
├── mcp_server.py            # MCP server component
├── prompts/                 # File-based prompt storage
│   ├── coding/
│   ├── writing/
│   └── analysis/
├── templates/
│   ├── base.html           # HTMX scripts + layout
│   ├── index.html          # Browse/search prompts
│   ├── create.html         # New prompt form
│   ├── view.html           # View single prompt
│   ├── edit.html           # Edit existing prompt
│   └── partials/           # HTMX fragments
└── static/css/style.css
```

## User Workflows

### Primary Use Cases

#### 1. Local Prompt Management
- Create, edit, and organize prompts in categories
- Search and filter prompt library
- Version history through file system
- Template variable support (`{{user_input}}`, `{{context}}`)

#### 2. MCP Integration
- Auto-start web interface when MCP server loads
- Claude/AI tools can access prompts via `mcp://promptbin/get-prompt/prompt-name`
- Seamless integration with AI workflows
- Auto-shutdown when MCP server stops

#### 3. Secure Sharing
- Generate shareable links for specific prompts
- One-click Dev Tunnel activation
- Automatic security protections against URL guessing
- Private-by-default with opt-in sharing

## Feature Specifications

### MVP Features

#### Core Prompt Management
- **Create prompts**: Split-pane editor with plain text input and live syntax-highlighted preview
- **Organize prompts**: File-based categories (coding/, writing/, analysis/)
- **Search functionality**: Live search with HTMX (keyup with 300ms delay)
- **Template variables**: Support for `{{variable}}` syntax with highlighting

#### MCP Server Integration
- **Auto-lifecycle**: Web server starts/stops with MCP server
- **Prompt access**: AI tools can fetch prompts via MCP protocol
- **Standalone mode**: Option to run web interface without MCP server

#### Sharing & Security
- **Dev Tunnel integration**: One-click tunnel start/stop
- **URL generation**: Copy buttons automatically use tunnel URLs when active
- **Access control**: Shared prompts use `/share/<token>/<prompt_id>` URLs
- **Rate limiting**: 5 failed attempts per IP kills tunnel automatically
- **Origin validation**: Only shared prompts accessible via tunnel

### User Interface

#### Layout Components
- **Header**: Logo, tunnel status indicator, search bar
- **Sidebar**: Category navigation, create new prompt button
- **Main content**: Prompt list/grid or editor view
- **Footer**: Tunnel controls (start/stop button, URL copying)

#### Editor Interface
- **Input pane**: Plain textarea for prompt editing
- **Preview pane**: Live syntax-highlighted preview
- **Metadata fields**: Title, category, description, tags
- **Action buttons**: Save, share, copy URL, delete

#### Prompt Display
- **Syntax highlighting**: Using highlight.js for markdown/prompt syntax
- **Template variables**: Special highlighting for `{{variables}}`
- **Copy functionality**: One-click copying of prompt content
- **Share controls**: Generate share link, tunnel status

### Technical Requirements

#### Performance
- **Startup time**: Web server starts in <2 seconds
- **Search response**: Live search results in <300ms
- **File operations**: Prompt save/load in <100ms
- **HTMX interactions**: No full page reloads for navigation

#### Security
- **Local-first**: No external data transmission by default
- **Tunnel isolation**: Only explicitly shared prompts accessible externally
- **Rate limiting**: Automatic tunnel shutdown after 5 failed attempts per IP
- **Token validation**: Cryptographically secure share tokens

#### Reliability
- **Graceful shutdown**: MCP server stop cleanly terminates web server
- **Error handling**: Clear error messages for file system issues
- **Recovery**: Automatic restart capabilities for both web and tunnel services

## Implementation Phases

### Phase 1: Core Local Functionality
- Basic Flask web interface
- File-based prompt storage
- HTMX interactions for smooth UX
- Search and categorization
- Split-pane editor with live preview

### Phase 2: MCP Integration
- MCP server implementation
- Auto-lifecycle management
- Prompt access protocol
- Standalone mode option

### Phase 3: Sharing & Security
- Dev Tunnel integration
- Share URL generation
- Rate limiting and security controls
- Tunnel management UI

### Phase 4: Polish & Enhancement
- Advanced syntax highlighting
- Improved search (tags, metadata)
- Export/import functionality
- Usage analytics

## Success Metrics
- **Adoption**: Number of active MCP integrations
- **Usage**: Prompts created/shared per user
- **Performance**: Average response times for key operations
- **Security**: Zero unauthorized access incidents
- **User satisfaction**: Positive feedback on local-first approach

## Technical Considerations

### Deployment
- Single Python package installation via `uv add promptbin`
- No external dependencies for core functionality
- Microsoft Dev Tunnels CLI required for sharing features
- Cross-platform compatibility (Windows, macOS, Linux)
- Modern Python dependency management with uv for fast, reliable installations

### Scalability
- File-based storage scales to thousands of prompts
- Local-first architecture eliminates server scaling concerns
- Dev Tunnels handle traffic bursts for sharing

### Maintenance
- Minimal infrastructure requirements
- File-based storage simplifies backups
- Version control friendly (git integration possible)
- Self-contained with no external service dependencies
