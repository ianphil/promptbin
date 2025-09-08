# Phase 2.1: Manager Refactoring

## Context
Refactor the core service managers (PromptManager, ShareManager, TunnelManager, FlaskManager) to accept configuration via dependency injection and implement the interfaces defined in Phase 1.3.

## Requirements
- Update all manager classes to implement their respective interfaces
- Remove hardcoded configuration and accept config via constructor
- Eliminate direct environment variable access
- Maintain backward compatibility during transition

## Current Issues to Address

### PromptManager (prompt_manager.py)
**Current Issues:**
- Hardcoded data directory: `Path(os.path.expanduser('~/promptbin-data'))` (line 23)
- Direct environment variable access through `data_dir` parameter
- No interface implementation

**Refactoring Tasks:**
- Implement `IPromptManager` interface
- Accept `PromptBinConfig` in constructor instead of `data_dir` string
- Remove direct `os.path.expanduser()` calls

### ShareManager (share_manager.py) 
**Current Issues:**
- Hardcoded default path: `"data/shares.json"` (line 17)
- No configuration injection
- No interface implementation

**Refactoring Tasks:**
- Implement `IShareManager` interface
- Accept `PromptBinConfig` in constructor
- Use config-provided paths instead of hardcoded defaults

### TunnelManager (tunnel_manager.py)
**Current Issues:**
- Direct environment variable access (lines 27-38)
- Hardcoded configuration values
- No interface implementation

**Refactoring Tasks:**
- Implement `ITunnelManager` interface  
- Accept `PromptBinConfig` and logger in constructor
- Remove all `os.environ.get()` calls

### FlaskManager (flask_manager.py)
**Current Issues:**
- Multiple constructor parameters instead of config object
- No interface implementation

**Refactoring Tasks:**
- Implement `IFlaskManager` interface
- Accept `PromptBinConfig` instead of individual parameters
- Simplify constructor signature

## Implementation Guidelines

### Constructor Patterns
**Before:**
```python
class PromptManager:
    def __init__(self, data_dir: Optional[str] = None):
        self.PROMPTS_DIR = Path(data_dir) if data_dir else Path(os.path.expanduser('~/promptbin-data'))
```

**After:**
```python
class PromptManager(IPromptManager):
    def __init__(self, config: PromptBinConfig):
        self.PROMPTS_DIR = Path(config.data_dir).expanduser()
        self.config = config
```

### Configuration Access Pattern
Replace scattered environment variable access:
```python
# Before
self._enabled = os.environ.get('DEVTUNNEL_ENABLED', 'true').lower() == 'true'

# After  
self._enabled = self.config.devtunnel_enabled
```

### Testing Requirements
- Unit tests for each manager with injected dependencies
- Integration tests with real vs mock dependencies
- Configuration injection tests
- Backward compatibility tests
- Error handling tests for invalid configurations

## Backward Compatibility Strategy
- Keep existing constructor signatures temporarily with deprecation warnings
- Support both old and new initialization patterns
- Provide clear migration path for existing code

## Success Criteria
- All managers implement their respective interfaces
- Configuration injected via constructor, no direct environment variable access
- Existing functionality preserved
- Comprehensive test coverage for refactored managers
- Clear separation between configuration and business logic