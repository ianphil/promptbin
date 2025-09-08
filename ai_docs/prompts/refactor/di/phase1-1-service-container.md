# Phase 1.1: Create Service Container

## Context
Implement a lightweight dependency injection container for PromptBin to replace global state management and enable proper service lifecycle management.

## Requirements
- Create `core/container.py` with a service container class
- Support singleton and transient service lifecycles
- Implement circular dependency detection
- Provide clear error messages for missing dependencies
- Enable interface-based service registration

## Implementation Guidelines

### Container Features
1. **Service Registration**: Register services by interface/class with factory functions
2. **Service Resolution**: Resolve dependencies recursively with proper lifecycle management
3. **Lifecycle Management**: Support singleton (shared instance) and transient (new instance per request)
4. **Circular Dependency Detection**: Detect and prevent infinite recursion in dependency graphs
5. **Error Handling**: Clear, actionable error messages for configuration issues

### API Design
```python
class ServiceContainer:
    def register_singleton(self, interface, implementation_factory)
    def register_transient(self, interface, implementation_factory)
    def resolve(self, interface)
    def is_registered(self, interface) -> bool
```

### Testing Requirements
- Unit tests for service registration and resolution
- Tests for singleton vs transient lifecycle behavior
- Circular dependency detection tests
- Error handling tests for missing dependencies
- Performance tests for service resolution

## Current Architecture Issues to Address
- Global variables in `app.py:25-43` (share_manager, prompt_manager, tunnel_manager)
- Direct instantiation throughout the codebase
- Hard-coded dependencies making testing difficult

## Success Criteria
- Container successfully manages service lifecycles
- Clear separation between service registration and resolution
- Comprehensive test coverage (100% for container core)
- No circular dependency issues
- Performance acceptable for application startup