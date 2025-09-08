# Dependency Injection Refactoring Prompts

This directory contains detailed implementation prompts for each phase of the PromptBin dependency injection refactoring as outlined in `@ai_docs/arch-refactor-di-plan.md`.

## Prompt Organization

### Phase 1: Core DI Infrastructure (High Priority)
1. **[Service Container](./phase1-1-service-container.md)** - Implement the core DI container
2. **[Configuration Management](./phase1-2-configuration-management.md)** - Centralize all environment variables  
3. **[Service Interfaces](./phase1-3-service-interfaces.md)** - Define contracts for all services

### Phase 2: Core Component Refactoring (High Priority)
1. **[Manager Refactoring](./phase2-1-manager-refactoring.md)** - Update service managers for DI
2. **[Flask App Refactoring](./phase2-2-flask-app-refactoring.md)** - Remove global state from Flask app
3. **[MCP Server Refactoring](./phase2-3-mcp-server-refactoring.md)** - Refactor MCP server to use container

### Phase 3: Integration and Testing (High Priority)  
1. **[CLI Integration](./phase3-1-cli-integration.md)** - Update CLI to configure and use container
2. **[Backwards Compatibility](./phase3-2-backwards-compatibility.md)** - Maintain compatibility during transition
3. **[Error Handling](./phase3-3-error-handling.md)** - Comprehensive error handling and logging

### Supporting Infrastructure
- **[Testing Infrastructure](./testing-infrastructure.md)** - Comprehensive testing strategy and mock implementations

## Usage Guidelines

### For Implementers
1. **Start with Phase 1** - Build the foundation first
2. **Follow the order** - Each phase builds on the previous
3. **Test thoroughly** - Use the testing infrastructure prompts
4. **Maintain compatibility** - Reference backwards compatibility guidelines

### For Each Prompt
- **Read the context** - Understand current issues and requirements
- **Follow implementation guidelines** - Specific patterns and examples provided
- **Apply testing requirements** - Each prompt includes testing guidance
- **Verify success criteria** - Clear measurable outcomes defined

## Key Principles

### Dependency Injection Benefits
- **Testability**: Easy to mock dependencies for unit testing
- **Maintainability**: Clear service boundaries and explicit dependencies
- **Flexibility**: Easy to swap implementations 
- **Configuration**: Centralized, validated configuration management
- **Debugging**: Clear service initialization and dependency resolution

### Implementation Strategy
- **Gradual Migration**: Support both old and new patterns during transition
- **Backward Compatibility**: Maintain existing APIs and environment variables
- **Error Handling**: Clear error messages and graceful degradation
- **Performance**: Ensure DI doesn't degrade application performance

## Files Created/Modified

### New Files (from prompts)
- `core/container.py` - Service container implementation
- `core/config.py` - Centralized configuration  
- `core/interfaces/*.py` - Service interface definitions
- `tests/unit/core/*` - Core infrastructure tests
- `tests/integration/*` - Integration tests
- `tests/fixtures/*` - Test utilities and mocks

### Modified Files (from prompts)
- `app.py` - Remove globals, add app factory
- `mcp_server.py` - Use container for dependencies
- `*_manager.py` - Accept config injection, implement interfaces
- `cli.py` - Configure and use container

## Success Metrics

### Code Quality
- Remove all global state management
- Clear separation of concerns
- Comprehensive test coverage (90%+ for new code)
- No circular dependencies

### Functionality
- All existing features work unchanged
- Performance equal to or better than current
- Clear error messages and graceful degradation
- Easy to add new services and features

### Developer Experience  
- Easy to test individual components
- Clear service boundaries and contracts
- Consistent configuration management
- Helpful error messages and logging

## Related Documentation
- `@ai_docs/arch-refactor.md` - Original architecture analysis
- `@ai_docs/arch-refactor-di-plan.md` - Overall implementation plan
- Project `CLAUDE.md` - PromptBin project overview and guidelines