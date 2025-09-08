# Phase 3.2: Backwards Compatibility

## Context
Ensure the dependency injection refactoring maintains full backward compatibility with existing APIs, environment variables, and user workflows during the transition period.

## Requirements
- Maintain all existing APIs and their behavior unchanged
- Support both old global access patterns and new DI during transition
- Preserve all current environment variable behavior  
- Provide clear migration path for any external integrations
- Ensure performance remains acceptable or improves

## Compatibility Areas to Preserve

### 1. Environment Variables
All existing environment variables must continue to work:

#### Flask/App Configuration
- `SECRET_KEY` - Flask secret key
- `FLASK_RUN_PORT` - Flask port (fallback)  
- `PROMPTBIN_PORT` - Primary port setting
- `PROMPTBIN_HOST` - Host binding
- `PROMPTBIN_DATA_DIR` - Data directory
- `PROMPTBIN_LOG_LEVEL` - Logging level

#### Tunnel Configuration  
- `DEVTUNNEL_ENABLED` - Enable/disable tunnels
- `DEVTUNNEL_AUTO_START` - Auto-start behavior
- `DEVTUNNEL_RATE_LIMIT` - Rate limiting threshold
- `DEVTUNNEL_RATE_WINDOW` - Rate limit window
- `DEVTUNNEL_LOG_LEVEL` - Tunnel logging level

### 2. CLI Interface
Preserve all existing CLI arguments and behavior:
- `promptbin` (default both mode)
- `promptbin --web` (web only)  
- `promptbin --mcp` (MCP only)
- All argument parsing and validation
- Same output messages and formatting

### 3. API Endpoints
All existing HTTP endpoints must work identically:
- `/` - Main page
- `/api/prompts` - CRUD operations
- `/api/search` - Search functionality
- `/api/share/*` - Sharing endpoints
- `/api/tunnel/*` - Tunnel management
- `/health` - Health checks
- `/mcp-status` - MCP status

### 4. MCP Protocol
All MCP resources and tools must function identically:
- `promptbin://list-prompts`
- `promptbin://get-prompt/{prompt_id}`
- `promptbin://get-prompt-by-name/{name}`
- `search_prompts` tool
- `flask_status` resource

## Implementation Strategy

### Dual Initialization Support
Support both old and new initialization patterns during transition:

```python
class PromptManager(IPromptManager):
    def __init__(self, config_or_data_dir=None):
        """Support both config object and legacy string data_dir"""
        if isinstance(config_or_data_dir, PromptBinConfig):
            # New DI pattern
            self.config = config_or_data_dir
            self.PROMPTS_DIR = Path(config_or_data_dir.data_dir).expanduser()
        else:
            # Legacy pattern - emit deprecation warning
            warnings.warn(
                "Passing data_dir string is deprecated. Use PromptBinConfig instead.",
                DeprecationWarning,
                stacklevel=2
            )
            data_dir = config_or_data_dir or os.path.expanduser('~/promptbin-data')
            self.PROMPTS_DIR = Path(data_dir)
            # Create minimal config for compatibility
            self.config = PromptBinConfig(data_dir=data_dir)
```

### Global Access Bridge
Maintain global accessor functions during transition:

```python
# In app.py - compatibility bridge
_global_container = None

def get_prompt_manager():
    """Legacy global access - deprecated but functional"""
    if _global_container:
        return _global_container.resolve(IPromptManager)
    else:
        # Fallback to old behavior with warning
        warnings.warn("Global access deprecated. Use dependency injection.", DeprecationWarning)
        return PromptManager()  # Old initialization
```

### Environment Variable Priority
Maintain existing environment variable precedence:

```python
class PromptBinConfig:
    @classmethod
    def from_environment(cls) -> "PromptBinConfig":
        """Load config with same precedence as original code"""
        return cls(
            flask_port=int(os.environ.get('PROMPTBIN_PORT', 
                          os.environ.get('FLASK_RUN_PORT', '5001'))),
            flask_host=os.environ.get('PROMPTBIN_HOST', '127.0.0.1'),
            secret_key=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
            # ... maintain exact same precedence
        )
```

### Testing Requirements
- **Regression Tests**: Comprehensive suite ensuring all existing functionality works
- **API Compatibility Tests**: Verify all endpoints return identical responses
- **Environment Variable Tests**: Confirm all env var combinations work as before
- **Migration Path Tests**: Test transition from old to new patterns
- **Performance Tests**: Ensure performance hasn't degraded

## Migration Path Documentation

### For External Integrations
Provide clear guidance for any external code:

```python
# Old pattern (still works with deprecation warning)
manager = PromptManager(data_dir="/custom/path")

# New recommended pattern  
config = PromptBinConfig(data_dir="/custom/path")
container = ServiceContainer()
container.register_singleton(PromptBinConfig, lambda: config)
container.register_singleton(IPromptManager, lambda: PromptManager(config))
manager = container.resolve(IPromptManager)
```

### Configuration Migration
```python
# Old environment variable usage (still works)
export PROMPTBIN_DATA_DIR=/custom/path
export DEVTUNNEL_ENABLED=false

# New pattern (environment variables automatically loaded)
config = PromptBinConfig.from_environment()  # Reads same env vars
```

## Deprecation Strategy

### Phase 1: Dual Support (Current)
- New DI system available
- Old patterns still work with deprecation warnings
- Documentation shows both approaches

### Phase 2: Deprecation Warnings (Next Release)
- Increase visibility of deprecation warnings
- Update documentation to prefer new patterns
- Provide migration tools/scripts

### Phase 3: Legacy Removal (Future Release)
- Remove deprecated global access patterns
- Keep environment variable support
- Maintain API compatibility

## Performance Considerations
- Container resolution should be as fast as global variable access
- Lazy initialization where appropriate  
- Service caching to avoid repeated resolution overhead
- Benchmark before/after to ensure no regression

## Success Criteria
- All existing functionality works without modification
- Performance equal to or better than current implementation
- Clear deprecation path with helpful warnings
- Comprehensive regression test coverage
- External integrations continue working without changes
- Environment variables maintain exact same precedence and behavior