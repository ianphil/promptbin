# Phase 3.1: CLI Integration

## Context
Update the CLI entry point (`cli.py`) to configure and use the dependency injection container, managing different service configurations for standalone vs MCP modes.

## Current Issues to Address

### Manual Service Management (cli.py:93-138)
```python
# Current approach: directly importing and calling main functions
def run_web_only(args):
    from app import main as app_main
    # Manual sys.argv manipulation
    
def run_mcp_only(args):
    from mcp_server import main as mcp_main
    # Manual environment variable setting

def run_both(args):
    from mcp_server import main as mcp_main
    # Manual environment variable setting
```

### Environment Variable Handling
- Direct `os.environ` manipulation (lines 115-118, 128-131)
- No centralized configuration management
- Inconsistent parameter passing

## Requirements
- Configure `ServiceContainer` based on command line arguments
- Register services with appropriate lifecycles for each mode
- Handle different service configurations for standalone vs MCP modes
- Eliminate direct environment variable manipulation
- Maintain all existing CLI functionality and options

## Implementation Guidelines

### Container Configuration by Mode

#### Standalone Web Mode
```python
def configure_standalone_container(args) -> ServiceContainer:
    """Configure container for standalone web interface"""
    container = ServiceContainer()
    
    # Create configuration from CLI args
    config = PromptBinConfig(
        flask_host=args.host,
        flask_port=args.port,
        data_dir=args.data_dir,
        log_level=args.log_level
    )
    
    # Register services for web-only mode
    container.register_singleton(PromptBinConfig, lambda: config)
    container.register_singleton(IPromptManager, lambda: PromptManager(config))
    container.register_singleton(IShareManager, lambda: ShareManager(config))
    container.register_singleton(ITunnelManager, lambda: TunnelManager(config))
    
    # No Flask manager needed in standalone mode
    return container
```

#### MCP Mode (with Flask subprocess)
```python
def configure_mcp_container(args) -> ServiceContainer:
    """Configure container for MCP server with Flask subprocess"""
    container = ServiceContainer()
    
    config = PromptBinConfig(
        flask_host=args.host,
        flask_port=args.port,
        data_dir=args.data_dir,
        log_level=args.log_level
    )
    
    # Register all services including FlaskManager
    container.register_singleton(PromptBinConfig, lambda: config)
    container.register_singleton(IPromptManager, lambda: PromptManager(config))
    container.register_singleton(IShareManager, lambda: ShareManager(config))
    container.register_singleton(ITunnelManager, lambda: TunnelManager(config))
    container.register_singleton(IFlaskManager, lambda: FlaskManager(config))
    
    return container
```

### Refactored Run Functions

#### Web Only Mode
```python
def run_web_only(args):
    """Run only the web interface using dependency injection"""
    container = configure_standalone_container(args)
    
    # Create Flask app with container
    app = create_app(container)
    
    print(f"🌐 Starting PromptBin web interface at http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=True)
```

#### MCP Only Mode  
```python
def run_mcp_only(args):
    """Run only the MCP server using dependency injection"""
    container = configure_mcp_container(args)
    
    # Create MCP server with container (no Flask subprocess)
    container.register_singleton(IFlaskManager, lambda: None)  # No Flask manager
    server = PromptBinMCPServer(container)
    
    print("🤖 Starting PromptBin MCP server...")
    return server.run()
```

#### Both Modes
```python
def run_both(args):
    """Run both MCP server and web interface"""
    container = configure_mcp_container(args)
    
    # Create MCP server with Flask subprocess capability
    server = PromptBinMCPServer(container)
    
    print("🚀 Starting PromptBin (MCP server + web interface)...")
    print(f"🤖 MCP server: Ready for AI tool connections")
    print(f"🌐 Web interface: Will be available at http://{args.host}:{args.port}")
    
    return server.run()
```

### Service Registration Strategy

#### Common Services (all modes)
- `PromptBinConfig`: Configuration object
- `IPromptManager`: Prompt storage and retrieval
- `IShareManager`: Share token management  
- `ITunnelManager`: Dev tunnels functionality

#### Mode-Specific Services
- **Standalone Mode**: No `IFlaskManager` (Flask runs directly)
- **MCP Mode**: `IFlaskManager` for subprocess management
- **Both Mode**: Full service registration

### Testing Requirements
- CLI argument parsing tests
- Container configuration tests for different modes
- Service registration verification tests  
- Mode-specific behavior tests
- Command line integration tests

## Environment Variable Elimination

### Before (lines 115-118)
```python
# Set environment variables for MCP server
os.environ['PROMPTBIN_HOST'] = args.host
os.environ['PROMPTBIN_PORT'] = str(args.port)
os.environ['PROMPTBIN_DATA_DIR'] = args.data_dir
os.environ['PROMPTBIN_LOG_LEVEL'] = args.log_level
```

### After
```python
# Create configuration object directly
config = PromptBinConfig(
    flask_host=args.host,
    flask_port=args.port,
    data_dir=args.data_dir,
    log_level=args.log_level
)
# Pass via dependency injection
```

## Backward Compatibility
- Maintain all existing CLI arguments and options
- Preserve existing behavior for each mode
- Keep same output messages and user experience
- Support environment variable overrides where appropriate

## Success Criteria
- All CLI modes use dependency injection container
- No direct environment variable manipulation in CLI code
- Service registration appropriate for each mode
- Existing CLI functionality preserved
- Clear separation between argument parsing and service configuration