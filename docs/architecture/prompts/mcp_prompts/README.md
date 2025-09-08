# MCP Server Implementation Prompts

This directory contains a complete set of implementation prompts for building PromptBin's MCP (Model Context Protocol) server integration. These prompts break down the complex MCP implementation into manageable, sequential phases.

## Overview

The MCP server implementation enables PromptBin to function in dual-mode:
- **Standalone Mode**: Independent Flask web application
- **MCP-Managed Mode**: MCP server automatically launches and manages the Flask web interface

This allows AI tools like Claude to access prompts via the MCP protocol while simultaneously providing a web interface for prompt management.

## Implementation Phases

### [Phase 1: Setup Dependencies & Structure](phase1_setup_dependencies.md)
**Focus**: Foundation and dependencies
- Research and integrate MCP Python SDK
- Create basic MCP server class structure  
- Set up logging and configuration systems
- Establish integration points with existing PromptManager

**Deliverables**: Basic `mcp_server.py` skeleton, updated dependencies, configuration system

### [Phase 2: Implement Core MCP Protocol](phase2_mcp_protocol.md)  
**Focus**: MCP protocol implementation
- Implement MCP server interface and message handling
- Create core endpoint handlers: `list_prompts()`, `get_prompt()`, `search_prompts()`
- Support protocol URLs: `mcp://promptbin/get-prompt/{prompt-name}`
- Template variable extraction and content analysis

**Deliverables**: Complete MCP protocol handlers, URL routing, response formatting

### [Phase 3: Flask Subprocess Integration](phase3_flask_subprocess.md)
**Focus**: Process management and lifecycle
- Auto-launch Flask app as subprocess on MCP server startup
- Health monitoring and automatic restart capabilities
- Graceful shutdown and resource cleanup
- Port management and configuration sharing

**Deliverables**: Robust subprocess management, health monitoring, clean lifecycle management

### [Phase 4: Advanced Features & Monitoring](phase4_advanced_features.md)
**Focus**: Production readiness and operations
- Advanced health monitoring and metrics
- Configuration management and environment detection
- Operational status endpoints and diagnostic tools
- Performance monitoring and resource management

**Deliverables**: Production-ready monitoring, observability, and operational features

## Usage Instructions

### Sequential Implementation
Work through the phases in order, as each phase builds on the previous ones:

1. Start with Phase 1 to establish the foundation
2. Implement Phase 2 for core MCP functionality
3. Add Phase 3 for Flask integration and process management
4. Complete with Phase 4 for production readiness

### Using with Claude Code
Use the `/review-prompt` command to analyze each phase:

```bash
# Review and plan a specific phase
/review-prompt ai_docs/prompts/mcp_prompts/phase1_setup_dependencies.md

# After completing each phase, move to the next
/review-prompt ai_docs/prompts/mcp_prompts/phase2_mcp_protocol.md
```

### Development Commands

Once implementation is complete, you'll have these usage modes:

```bash
# Standalone Flask app (current mode)
python app.py

# MCP server mode (launches Flask automatically)
python mcp_server.py

# Development with verbose logging
PROMPTBIN_LOG_LEVEL=DEBUG python mcp_server.py
```

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                MCP Client                       │
│           (Claude, other AI tools)              │
└─────────────────┬───────────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────────┐
│              MCP Server                         │
│  ┌─────────────────────────────────────────┐    │
│  │         Protocol Handlers               │    │
│  │  • list_prompts()                       │    │
│  │  • get_prompt(id)                       │    │
│  │  • search_prompts(query)                │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │       Flask Manager                     │    │
│  │  • Subprocess control                   │    │
│  │  • Health monitoring                    │    │
│  │  • Auto-restart                         │    │
│  └─────────────────────────────────────────┘    │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/Process
┌─────────────────▼───────────────────────────────┐
│              Flask Web App                      │
│  • HTMX templates and UI                       │
│  • REST API endpoints                          │
│  • Share functionality                         │
│  • Prompt management interface                 │
└─────────────────┬───────────────────────────────┘
                  │ File I/O
┌─────────────────▼───────────────────────────────┐
│            PromptManager                        │
│  • File-based storage                          │
│  • CRUD operations                             │
│  • Search functionality                        │
└─────────────────────────────────────────────────┘
```

## Key Design Principles

### Dual-Mode Operation
- **Standalone Flask**: Works independently without MCP server
- **MCP-Managed**: MCP server controls Flask lifecycle automatically
- **Shared Data**: Both modes use the same PromptManager and data files

### Process Isolation  
- **Separate processes**: MCP server and Flask run in separate processes
- **Fault tolerance**: Flask crashes don't affect MCP server
- **Resource isolation**: Clear separation of concerns and resources

### Configuration Sharing
- **Unified config**: Shared configuration system between both components
- **Environment detection**: Automatic detection of runtime mode
- **Dynamic updates**: Configuration changes without restarts

## Testing Strategy

Each phase includes specific testing requirements:

- **Unit tests**: Individual component functionality
- **Integration tests**: Cross-component interactions  
- **Process tests**: Subprocess lifecycle and monitoring
- **Protocol tests**: MCP protocol compliance and compatibility
- **Failure tests**: Error handling and recovery scenarios

## Success Criteria

The completed MCP implementation should achieve:

✅ **Functional Requirements**
- AI tools can connect and access prompts via MCP protocol
- Flask web interface launches automatically with MCP server
- Clean shutdown with no orphaned processes
- Robust error handling and recovery

✅ **Non-Functional Requirements**  
- Production-ready reliability and monitoring
- Comprehensive logging and observability
- Efficient resource usage and performance
- Clear operational procedures and diagnostics

## Related Documentation

- [Original MCP Server Prompt](../06_create_mcp_server.md) - Initial requirements
- [Implementation Plan](../06a_mcp_implementation_plan.md) - High-level analysis and planning
- [Auto-Lifecycle Management](../07_implement_auto_lifecycle.md) - Next phase requirements

## Notes

- Each phase prompt is self-contained but builds on previous phases
- Phases can be implemented over multiple development sessions
- Focus on one phase at a time for clarity and testability
- Document design decisions and implementation notes as you progress
- Test thoroughly at each phase before moving to the next