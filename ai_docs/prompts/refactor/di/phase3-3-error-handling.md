# Phase 3.3: Error Handling

## Context
Implement comprehensive error handling for the dependency injection system, including clear error messages, graceful degradation, and robust logging integration.

## Requirements
- Clear error messages for missing dependencies and circular references
- Graceful degradation when optional services aren't available
- Comprehensive logging of service lifecycle events
- Recovery mechanisms for common error scenarios
- User-friendly error reporting

## Error Scenarios to Handle

### 1. Container Configuration Errors

#### Missing Dependencies
```python
class ServiceResolutionError(Exception):
    """Raised when a required service cannot be resolved"""
    def __init__(self, service_type, available_services):
        self.service_type = service_type
        self.available_services = available_services
        super().__init__(self._create_message())
    
    def _create_message(self):
        return (f"Cannot resolve service '{self.service_type.__name__}'. "
                f"Available services: {[s.__name__ for s in self.available_services]}")
```

#### Circular Dependencies
```python
class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected"""
    def __init__(self, dependency_chain):
        self.dependency_chain = dependency_chain
        super().__init__(self._create_message())
    
    def _create_message(self):
        chain = " -> ".join(service.__name__ for service in self.dependency_chain)
        return f"Circular dependency detected: {chain} -> {self.dependency_chain[0].__name__}"
```

### 2. Configuration Validation Errors

#### Invalid Configuration Values
```python
class ConfigurationError(Exception):
    """Raised when configuration validation fails"""
    def __init__(self, field_name, value, reason):
        self.field_name = field_name
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid configuration for '{field_name}': {value} - {reason}")
```

#### Missing Required Configuration
```python
class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing"""
    def __init__(self, field_name):
        super().__init__(field_name, None, "Required configuration missing")
```

### 3. Service Initialization Errors

#### Service Creation Failures
```python
class ServiceInitializationError(Exception):
    """Raised when service initialization fails"""
    def __init__(self, service_type, original_exception):
        self.service_type = service_type
        self.original_exception = original_exception
        super().__init__(self._create_message())
    
    def _create_message(self):
        return (f"Failed to initialize service '{self.service_type.__name__}': "
                f"{type(self.original_exception).__name__}: {self.original_exception}")
```

## Error Handling Implementation

### Container Error Handling
```python
class ServiceContainer:
    def resolve(self, service_type):
        """Resolve service with comprehensive error handling"""
        try:
            if service_type in self._resolving:
                # Circular dependency detected
                chain = list(self._resolving) + [service_type]
                raise CircularDependencyError(chain)
            
            if service_type not in self._services:
                available = list(self._services.keys())
                raise ServiceResolutionError(service_type, available)
            
            self._resolving.add(service_type)
            try:
                service = self._create_service(service_type)
                return service
            finally:
                self._resolving.remove(service_type)
                
        except Exception as e:
            self._logger.error(f"Service resolution failed: {e}")
            raise
```

### Configuration Error Handling
```python
class PromptBinConfig:
    def validate(self) -> None:
        """Validate configuration with detailed error messages"""
        errors = []
        
        # Port validation
        if not (1024 <= self.flask_port <= 65535):
            errors.append(ConfigurationError(
                'flask_port', self.flask_port, 
                'Port must be between 1024 and 65535'
            ))
        
        # Directory validation
        try:
            data_path = Path(self.data_dir).expanduser()
            if not data_path.parent.exists():
                errors.append(ConfigurationError(
                    'data_dir', self.data_dir,
                    f'Parent directory does not exist: {data_path.parent}'
                ))
        except Exception as e:
            errors.append(ConfigurationError(
                'data_dir', self.data_dir,
                f'Invalid path: {e}'
            ))
        
        if errors:
            raise ConfigurationError("Configuration validation failed", errors, "")
```

## Graceful Degradation Strategy

### Optional Service Handling
```python
class ServiceContainer:
    def try_resolve(self, service_type, default=None):
        """Try to resolve service, return default if unavailable"""
        try:
            return self.resolve(service_type)
        except ServiceResolutionError:
            self._logger.warning(f"Optional service {service_type.__name__} not available, using default")
            return default
```

### Feature Degradation Examples
```python
def create_app(container: ServiceContainer) -> Flask:
    """Create Flask app with graceful degradation"""
    app = Flask(__name__)
    
    # Required services
    prompt_manager = container.resolve(IPromptManager)
    
    # Optional services with degradation
    tunnel_manager = container.try_resolve(ITunnelManager)
    if not tunnel_manager:
        app.logger.warning("Tunnel functionality disabled - ITunnelManager not available")
        # Disable tunnel-related routes
    
    share_manager = container.try_resolve(IShareManager)
    if not share_manager:
        app.logger.warning("Sharing functionality disabled - IShareManager not available")
        # Disable sharing routes
```

### Partial Functionality Mode
```python
class PromptBinMCPServer:
    def __init__(self, container: ServiceContainer):
        """Initialize with graceful degradation for optional services"""
        self.container = container
        
        # Required services - fail hard if missing
        self.prompt_manager = container.resolve(IPromptManager)
        
        # Optional services - degrade gracefully
        try:
            self.flask_manager = container.resolve(IFlaskManager)
            self.flask_enabled = True
        except ServiceResolutionError:
            self.flask_manager = None
            self.flask_enabled = False
            self.logger.warning("Flask web interface disabled - IFlaskManager not available")
```

## Logging Integration

### Service Lifecycle Logging
```python
class ServiceContainer:
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.ServiceContainer")
        
    def register_singleton(self, interface, factory):
        self._logger.debug(f"Registering singleton service: {interface.__name__}")
        # ... registration logic
        
    def resolve(self, service_type):
        self._logger.debug(f"Resolving service: {service_type.__name__}")
        service = self._create_service(service_type)
        self._logger.info(f"Service resolved successfully: {service_type.__name__}")
        return service
```

### Error Context Logging
```python
class ErrorHandler:
    @staticmethod
    def log_startup_error(logger, error, context):
        """Log startup errors with context"""
        logger.error(f"Startup failed in {context}: {error}")
        logger.debug("Error details:", exc_info=True)
        
        # Provide helpful suggestions
        if isinstance(error, ServiceResolutionError):
            logger.error("Suggestion: Check service registration in container setup")
        elif isinstance(error, ConfigurationError):
            logger.error("Suggestion: Verify environment variables and configuration")
```

## Recovery Mechanisms

### Automatic Retry
```python
def with_retry(max_attempts=3, delay=1.0):
    """Decorator for automatic retry on transient failures"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator
```

### Fallback Configuration
```python
class ConfigManager:
    @staticmethod
    def load_with_fallbacks():
        """Load configuration with multiple fallback strategies"""
        try:
            return PromptBinConfig.from_environment()
        except ConfigurationError as e:
            logger.warning(f"Environment configuration failed: {e}")
            try:
                return PromptBinConfig.from_file("promptbin.conf")
            except Exception:
                logger.warning("File configuration failed, using defaults")
                return PromptBinConfig()  # All defaults
```

## Testing Requirements
- Exception handling tests for all error scenarios
- Graceful degradation behavior tests  
- Logging output verification tests
- Error message clarity and helpfulness tests
- Recovery mechanism effectiveness tests

## User Experience Considerations
- Error messages should be actionable and helpful
- Logs should provide debugging information without overwhelming users
- Graceful degradation should maintain core functionality
- Recovery suggestions should be specific and practical

## Success Criteria
- Clear, actionable error messages for all failure scenarios
- No silent failures or undefined behavior
- Graceful degradation maintains core functionality
- Comprehensive logging aids debugging
- Recovery mechanisms handle transient failures effectively