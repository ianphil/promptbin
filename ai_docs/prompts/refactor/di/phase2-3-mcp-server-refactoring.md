# Phase 2.3: MCP Server Refactoring

## Context
Refactor the MCP server (`mcp_server.py`) to use the dependency injection container instead of directly instantiating services, creating clear separation between protocol handling and service management.

## Current Issues to Address

### Direct Service Instantiation (mcp_server.py:26-33)
```python
# Current problematic direct instantiation
def __init__(self, config: Optional[Dict[str, Any]] = None):
    self.config = config or self._load_default_config()
    self.mcp = FastMCP("PromptBin")
    self.prompt_manager = PromptManager(data_dir=self.config['data_dir'])  # Direct instantiation
    self.flask_process = None
    self.is_running = False
    self.flask_manager = None
```

### Flask Manager Setup (lines 51-65)
```python
# Direct instantiation of FlaskManager
from flask_manager import FlaskManager
self.flask_manager = FlaskManager(
    host=self.config['flask_host'],
    base_port=self.config['flask_port'],
    # ... multiple parameters
)
```

### Configuration Management
- Mixed hardcoded configuration and parameter passing
- No centralized configuration management
- Direct environment variable access in some areas

## Requirements
- Accept `ServiceContainer` in constructor instead of config dictionary
- Use container to resolve all service dependencies
- Remove direct service instantiation
- Clean separation: MCP server handles protocol, container manages lifecycle
- Maintain all existing MCP protocol functionality

## Implementation Guidelines

### Constructor Refactoring
**Before:**
```python
class PromptBinMCPServer:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.prompt_manager = PromptManager(data_dir=self.config['data_dir'])
        # ... direct instantiation
```

**After:**
```python
class PromptBinMCPServer:
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.config = container.resolve(PromptBinConfig)
        self.prompt_manager = container.resolve(IPromptManager)
        self.flask_manager = container.resolve(IFlaskManager)
        # ... all services from container
```

### Service Access Pattern
Replace direct service access with container resolution:
```python
# Before
prompt = self.prompt_manager.get_prompt(resolved_id)

# After  
prompt_manager = self.container.resolve(IPromptManager)
prompt = prompt_manager.get_prompt(resolved_id)
```

### MCP Handler Updates
Update all MCP protocol handlers to use container-resolved services:
- `list_all_prompts()` 
- `get_single_prompt(prompt_id)`
- `search_prompts(query, category, limit)`
- `get_prompt_by_name(name)`
- `flask_status()`

### Testing Requirements
- MCP server initialization tests with container
- Protocol handler tests with mocked services  
- Service lifecycle management tests
- MCP protocol compliance tests
- Container integration tests

## Flask Manager Integration

### Current Setup (lines 344-346)
```python
if server.flask_manager:
    asyncio.run(server.flask_manager.start_flask())
    server.logger.info(f"Flask web interface started at http://{server.config['flask_host']}:{server.flask_manager.port}")
```

### Refactored Approach
```python
flask_manager = container.resolve(IFlaskManager)
if flask_manager:
    asyncio.run(flask_manager.start_flask())
    config = container.resolve(PromptBinConfig)
    server.logger.info(f"Flask web interface started at http://{config.flask_host}:{flask_manager.port}")
```

## Configuration Handling

### Remove Hardcoded Config (lines 67-77)
Replace `_load_default_config()` method with proper configuration injection:
```python
# Remove this method entirely
def _load_default_config(self) -> Dict[str, Any]:
    return {
        'mode': 'mcp-managed',
        'flask_port': 5001,
        # ... hardcoded values
    }
```

Configuration should come from `PromptBinConfig` via container.

## Main Function Updates

### Current main() (lines 337-368)
```python
def main():
    server = PromptBinMCPServer()  # No container
    # ... manual service management
```

### Refactored main()
```python
def main():
    # Create and configure container
    container = ServiceContainer()
    config = PromptBinConfig.from_environment()
    
    # Register services
    container.register_singleton(PromptBinConfig, lambda: config)
    container.register_singleton(IPromptManager, lambda: PromptManager(config))
    # ... register all services
    
    # Create server with container
    server = PromptBinMCPServer(container)
    # ... rest of startup logic
```

## Success Criteria
- MCP server receives all dependencies via container
- No direct service instantiation in MCP server code
- All MCP protocol handlers work with container-resolved services  
- Flask subprocess management works correctly with DI
- Comprehensive test coverage with mocked services
- Clear separation between protocol handling and service management