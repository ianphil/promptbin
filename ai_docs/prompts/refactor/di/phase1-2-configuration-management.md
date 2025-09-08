# Phase 1.2: Configuration Management

## Context
Create a centralized configuration system to replace scattered `os.environ.get()` calls throughout the PromptBin codebase with a unified, validated configuration management approach.

## Requirements
- Create `core/config.py` with a centralized configuration class
- Consolidate all environment variables from across the codebase
- Add validation and sensible defaults for all configuration options
- Support dependency injection of configuration into services

## Current Environment Variables to Consolidate
From codebase analysis:
- `SECRET_KEY`, `FLASK_RUN_PORT` (app.py)
- `PROMPTBIN_PORT`, `PROMPTBIN_HOST`, `PROMPTBIN_DATA_DIR`, `PROMPTBIN_LOG_LEVEL` (various files)
- `DEVTUNNEL_ENABLED`, `DEVTUNNEL_AUTO_START`, `DEVTUNNEL_RATE_LIMIT`, `DEVTUNNEL_RATE_WINDOW`, `DEVTUNNEL_LOG_LEVEL` (tunnel_manager.py)

## Implementation Guidelines

### Configuration Class Design
```python
@dataclass
class PromptBinConfig:
    # Flask configuration
    flask_host: str = "127.0.0.1"
    flask_port: int = 5001
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Data configuration
    data_dir: str = "~/promptbin-data"
    log_level: str = "INFO"
    
    # Tunnel configuration
    devtunnel_enabled: bool = True
    devtunnel_auto_start: bool = False
    devtunnel_rate_limit: int = 5
    devtunnel_rate_window: int = 30
    
    @classmethod
    def from_environment(cls) -> "PromptBinConfig"
    def validate(self) -> None
```

### Features Required
1. **Environment Variable Loading**: Read from environment with proper type conversion
2. **Validation**: Ensure all configuration values are valid (ports in range, directories exist, etc.)
3. **Defaults**: Sensible defaults for all optional configuration
4. **Type Safety**: Proper type hints and runtime type checking
5. **Serialization**: Support for configuration export/import for testing

### Testing Requirements
- Unit tests for configuration validation and defaults
- Tests for environment variable precedence
- Invalid configuration handling tests
- Configuration serialization/deserialization tests
- Environment variable mocking tests

## Areas to Refactor
Replace direct environment variable access in:
- `app.py` (lines 20, 41, various routes)
- `mcp_server.py` (lines 74-77)
- `tunnel_manager.py` (lines 27-38)
- `cli.py` (lines 79, 115-118)

## Success Criteria
- All environment variables accessed through centralized config
- Configuration validation prevents invalid states
- Easy to modify configuration for testing
- Clear documentation of all configuration options
- Backward compatibility with existing environment variables