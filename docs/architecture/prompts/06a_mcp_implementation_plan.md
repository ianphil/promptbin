# Prompt 06a: MCP Server Implementation Plan

## Current State Analysis

### ✅ What's Already Implemented:
- **Flask Web App**: Fully functional with HTMX templates, prompt management, sharing system
- **File-Based Storage**: Complete PromptManager with CRUD operations 
- **Share System**: Token-based sharing with public URLs
- **Core Infrastructure**: Ready to integrate with MCP server

### ❌ What's Missing (Gap Analysis):
- **MCP Server Component**: No `mcp_server.py` exists yet
- **MCP Dependencies**: No MCP-specific libraries in `pyproject.toml`
- **Process Management**: No subprocess handling for Flask app
- **MCP Protocol Implementation**: No MCP endpoints or protocol handlers
- **Lifecycle Management**: No auto-start/stop coordination

## Technical Requirements Analysis

### 1. MCP Protocol Implementation
**Requirement**: Implement Model Context Protocol server that AI tools like Claude can load
- Need MCP Python SDK (likely `mcp` or `model-context-protocol` package)
- Must implement standard MCP server interface
- Handle MCP message routing and responses

### 2. Required MCP Endpoints
**Requirement**: `list_prompts()`, `get_prompt(prompt_id)`, `search_prompts(query)`
- **list_prompts()**: Return all available prompts with metadata
- **get_prompt(prompt_id)**: Retrieve specific prompt content
- **search_prompts(query)**: Search functionality integration
- **Protocol URLs**: Support `mcp://promptbin/get-prompt/{prompt-name}` format

### 3. Subprocess Management
**Requirement**: Auto-launch Flask app and monitor it
- Start Flask as subprocess on MCP server initialization
- Monitor Flask process health and restart if crashed
- Clean shutdown of Flask when MCP server stops
- Handle port conflicts and process cleanup

### 4. Error Handling & Logging
**Requirement**: Robust error handling and logging
- MCP protocol error responses
- Flask subprocess monitoring and restart logic
- Graceful degradation when Flask is unavailable
- Comprehensive logging for debugging

## Implementation Plan

### Phase 1: Setup MCP Dependencies & Structure
1. **Add MCP dependency** to `pyproject.toml`
   - Research and add appropriate MCP Python package
   - Ensure compatibility with existing Flask dependencies

2. **Create `mcp_server.py` skeleton**
   - MCP server class structure
   - Basic initialization and shutdown methods
   - Logging setup

### Phase 2: Implement Core MCP Protocol
1. **Implement MCP server interface**
   - Handle MCP protocol initialization
   - Set up message handling and routing
   - Error response formatting

2. **Create MCP endpoint handlers**
   - `list_prompts()`: Interface with existing PromptManager
   - `get_prompt(prompt_id)`: Retrieve and format prompt content  
   - `search_prompts(query)`: Integrate existing search functionality
   - Handle prompt name resolution for protocol URLs

### Phase 3: Flask Subprocess Integration
1. **Implement Flask lifecycle management**
   - Start Flask app as subprocess on MCP server init
   - Monitor Flask process health with periodic checks
   - Automatic restart logic for crashed Flask processes
   - Clean shutdown sequence

2. **Process coordination**
   - Shared configuration between MCP and Flask
   - Port management and conflict resolution
   - Environment variable coordination

### Phase 4: Advanced Features
1. **Health monitoring**
   - HTTP health checks to Flask app
   - Process monitoring and restart logic
   - Performance metrics and logging

2. **Configuration & Environment Detection**
   - Detect if running in MCP mode vs standalone
   - Shared config files or environment variables
   - Status endpoints for mode detection

## Technical Considerations

### Dependencies
- **MCP SDK**: Need to research official Python MCP library
- **Process Management**: Use `subprocess` and `psutil` for robust process handling  
- **HTTP Client**: `requests` for health checks to Flask app
- **Async Support**: May need `asyncio` if MCP requires async handlers

### Architecture Decisions  
- **Port Strategy**: Default Flask to 5000, with fallback port detection
- **Data Sharing**: Both MCP and Flask will use same PromptManager instance
- **Error Handling**: MCP server remains functional even if Flask crashes
- **Logging**: Unified logging strategy across both components

### Security & Reliability
- **Process Isolation**: Flask runs as separate process for stability
- **Resource Cleanup**: Ensure no zombie processes on shutdown
- **Error Recovery**: Graceful degradation and restart capabilities
- **Configuration Validation**: Validate shared config on startup

## Estimated Scope
- **Complexity**: Medium-High (subprocess management + protocol implementation)
- **Development Time**: 2-3 focused sessions
- **Testing Requirements**: Extensive process lifecycle testing needed
- **Documentation**: Will need MCP server configuration instructions

This implementation will complete the dual-mode architecture vision, allowing PromptBin to function both as a standalone web app and as an MCP-integrated tool for AI assistants.