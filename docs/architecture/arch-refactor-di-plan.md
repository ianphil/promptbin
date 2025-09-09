# Dependency Injection Implementation Plan with Testing

## Phase 1: Core DI Infrastructure (High Priority)

### 1.1 Create Service Container
- **Create `src/promptbin/core/container.py`**: Lightweight DI container with service registration and resolution
- **Features**: Singleton/transient lifecycle management, circular dependency detection, interface-based registration

**Testing Plan:**
- Unit tests for service registration and resolution
- Tests for singleton vs transient lifecycle behavior
- Circular dependency detection tests
- Error handling tests for missing dependencies
- Performance tests for service resolution

### 1.2 Configuration Management  
- **Create `src/promptbin/core/config.py`**: Centralized configuration class that consolidates all environment variables
- **Replace scattered `os.environ.get()` calls** with config injection
- **Add validation and defaults** for all configuration options

**Testing Plan:**
- Unit tests for configuration validation and defaults
- Tests for environment variable precedence
- Invalid configuration handling tests
- Configuration serialization/deserialization tests
- Environment variable mocking tests

### 1.3 Service Interfaces
- **Create `core/interfaces/`**: Abstract base classes for all major services
- **Define contracts**: `IPromptManager`, `IShareManager`, `ITunnelManager`, `IFlaskManager`
- **Enable testing** with mock implementations

**Testing Plan:**
- Interface compliance tests for all implementations
- Mock service implementations for testing
- Contract verification tests
- Interface method signature validation

## Phase 2: Refactor Core Components (High Priority)

### 2.1 Manager Refactoring
- **Update `PromptManager`**: Accept config via constructor, implement interface
- **Update `ShareManager`**: Remove hardcoded paths, accept config injection  
- **Update `TunnelManager`**: Accept config and logger via constructor
- **Update `FlaskManager`**: Accept all dependencies via constructor

**Testing Plan:**
- Unit tests for each manager with injected dependencies
- Integration tests with real vs mock dependencies
- Configuration injection tests
- Backward compatibility tests
- Error handling tests for invalid configurations

### 2.2 Flask App Refactoring
- **Remove global variables**: Replace global managers in `src/promptbin/app.py:25-43` with dependency injection
- **Create app factory**: `create_app(container)` function that receives configured services
- **Update route handlers**: Access services through dependency injection instead of globals

**Testing Plan:**
- Flask app factory tests with different container configurations
- Route handler tests with mocked services
- Integration tests for full request/response cycles
- Global state elimination verification tests
- Flask test client integration with DI container

### 2.3 MCP Server Refactoring  
- **Update `PromptBinMCPServer.__init__()`**: Accept container instead of direct dependencies
- **Remove direct instantiation**: Use container to resolve all service dependencies
- **Clean separation**: MCP server focuses on protocol, container manages lifecycle

**Testing Plan:**
- MCP server initialization tests with container
- Protocol handler tests with mocked services
- Service lifecycle management tests
- MCP protocol compliance tests
- Container integration tests

## Phase 3: Integration and Testing (High Priority)

### 3.1 CLI Integration
- **Update `src/promptbin/cli.py`**: Configure container based on command line arguments
- **Service registration**: Register all services with appropriate lifecycles  
- **Mode handling**: Different service configurations for standalone vs MCP modes

**Testing Plan:**
- CLI argument parsing tests
- Container configuration tests for different modes
- Service registration verification tests
- Mode-specific behavior tests
- Command line integration tests

### 3.2 Backwards Compatibility
- **Maintain existing APIs**: Ensure existing functionality works unchanged
- **Gradual migration**: Support both old global access and new DI during transition
- **Environment variable support**: Preserve all current environment variable behavior

**Testing Plan:**
- Comprehensive regression tests for existing functionality
- API compatibility tests
- Environment variable behavior preservation tests
- Migration path verification tests
- Performance comparison tests (before/after DI)

### 3.3 Error Handling
- **Container exceptions**: Clear error messages for missing dependencies or circular references
- **Graceful degradation**: Fallback behavior when optional services aren't available
- **Logging integration**: Comprehensive logging of service lifecycle events

**Testing Plan:**
- Exception handling tests for all error scenarios
- Graceful degradation behavior tests
- Logging output verification tests
- Error message clarity tests
- Recovery mechanism tests

## Testing Infrastructure

### Test Organization
- `tests/unit/core/` - Container, config, interface tests
- `tests/unit/services/` - Individual service tests with mocks
- `tests/integration/` - Cross-service integration tests
- `tests/e2e/` - End-to-end application tests
- `tests/fixtures/` - Test data and mock implementations

### Test Coverage Requirements
- Minimum 90% code coverage for new DI infrastructure
- 100% coverage for container and configuration classes
- Integration test coverage for all service interactions
- Performance benchmark tests for service resolution

### Testing Tools and Frameworks
- **pytest** for test framework
- **pytest-mock** for mocking dependencies
- **pytest-cov** for coverage reporting
- **pytest-benchmark** for performance testing
- **factory_boy** for test data generation

## Implementation Benefits

1. **Testability**: Easy to mock dependencies for unit testing
2. **Maintainability**: Clear service boundaries and explicit dependencies  
3. **Flexibility**: Easy to swap implementations (e.g., different storage backends)
4. **Configuration**: Centralized, validated configuration management
5. **Debugging**: Clear service initialization and dependency resolution logging

## Files to Create/Modify

**New Files:**
- `src/promptbin/core/container.py` (DI container implementation)
- `src/promptbin/core/config.py` (centralized configuration)
- `src/promptbin/core/interfaces/__init__.py` (service interfaces)
- `tests/unit/core/test_container.py`
- `tests/unit/core/test_config.py`
- `tests/unit/services/test_*_manager.py`
- `tests/integration/test_service_integration.py`

**Modified Files:**  
- `src/promptbin/app.py` (remove globals, add app factory)
- `src/promptbin/mcp/server.py` (use container for dependencies)
- `src/promptbin/managers/prompt_manager.py` (accept config injection)
- `src/promptbin/managers/share_manager.py` (accept config injection)  
- `src/promptbin/managers/tunnel_manager.py` (accept config injection)
- `src/promptbin/utils/flask_manager.py` (accept config injection)
- `src/promptbin/cli.py` (configure and use container)

This plan maintains existing functionality while establishing a solid foundation for future architectural improvements, with comprehensive testing at every level.