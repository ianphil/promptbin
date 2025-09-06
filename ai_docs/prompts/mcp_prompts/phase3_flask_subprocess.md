# Phase 3: Flask Subprocess Integration

## Overview
Implement robust subprocess management for the Flask web application, allowing the MCP server to automatically launch, monitor, and manage the Flask app lifecycle.

## Prerequisites
- Phase 1 & 2 completed: MCP server with protocol handlers working
- Flask app (`app.py`) fully functional as standalone application
- Process management dependencies installed (`psutil`)

## Requirements

### 1. Flask Lifecycle Management

#### Subprocess Startup
- **Launch Flask app**: Start Flask as subprocess when MCP server initializes
- **Port management**: 
  - Default to port 5000
  - Detect port conflicts and find alternative ports
  - Pass port configuration to Flask app
- **Environment setup**:
  - Pass necessary environment variables to Flask subprocess
  - Configure Flask for production mode when running under MCP
  - Set appropriate logging levels

#### Process Monitoring
- **Health checks**: Periodic HTTP health checks to Flask app
- **Process monitoring**: Monitor Flask process status using `psutil`
- **Automatic restart**: Restart Flask if it becomes unresponsive or crashes
- **Resource monitoring**: Track memory and CPU usage of Flask subprocess

#### Graceful Shutdown
- **Clean termination**: Send SIGTERM to Flask process on MCP server shutdown
- **Timeout handling**: Force kill (SIGKILL) if Flask doesn't shut down gracefully
- **Resource cleanup**: Ensure no zombie processes or resource leaks
- **Data consistency**: Ensure any in-flight requests are handled appropriately

### 2. Process Coordination

#### Configuration Sharing
Create a shared configuration system between MCP server and Flask app:
- **Config file**: JSON or YAML configuration file both processes can read
- **Environment variables**: Standardized env vars for shared settings
- **Runtime parameters**: Port, debug mode, logging level, data directory

#### Inter-Process Communication
- **Health endpoint**: Flask app exposes `/health` endpoint for MCP server checks
- **Status endpoint**: Flask app exposes `/mcp-status` to indicate MCP integration mode
- **Graceful restart**: Mechanism for MCP server to trigger Flask restarts

#### Data Synchronization
- **Shared storage**: Both processes access same PromptManager data files
- **File locking**: Prevent concurrent write conflicts
- **Change notifications**: Optional file system watching for real-time updates

### 3. Implementation Details

#### FlaskManager Class
```python
class FlaskManager:
    def __init__(self, config):
        self.config = config
        self.process = None
        self.port = None
        self.health_check_url = None
        
    async def start_flask(self):
        # Find available port
        # Start Flask subprocess  
        # Wait for Flask to become ready
        # Begin health monitoring
        
    async def stop_flask(self):
        # Send graceful shutdown signal
        # Wait for clean termination
        # Force kill if necessary
        # Clean up resources
        
    async def restart_flask(self):
        # Stop current instance
        # Start new instance
        # Update health check URL
        
    def is_healthy(self):
        # HTTP health check to Flask
        # Process status check
        # Return combined health status
        
    async def monitor_loop(self):
        # Continuous monitoring loop
        # Restart on failures
        # Log health status changes
```

#### Health Check Implementation
- **HTTP endpoint**: `GET /health` returns JSON with server status
- **Response format**:
  ```json
  {
    "status": "healthy",
    "uptime": 3600,
    "mode": "mcp-managed",
    "version": "0.1.0",
    "prompts_count": 42
  }
  ```
- **Timeout handling**: Reasonable timeouts for health checks
- **Retry logic**: Multiple attempts before marking as unhealthy

#### Port Management
```python
def find_available_port(start_port=5000):
    # Check if port is available
    # Return first available port
    # Handle port conflicts gracefully
    
def configure_flask_port(port):
    # Set environment variable for Flask
    # Update configuration files
    # Pass port to subprocess
```

### 4. Error Handling & Recovery

#### Failure Scenarios
- **Flask startup failure**: Log error, attempt alternative port, notify MCP clients
- **Flask crash during operation**: Automatic restart with backoff strategy
- **Health check failures**: Distinguish between temporary and persistent issues
- **Resource exhaustion**: Handle memory/CPU limits gracefully

#### Recovery Strategies
- **Exponential backoff**: Increasing delays between restart attempts
- **Failure thresholds**: Maximum restart attempts before giving up
- **Graceful degradation**: MCP server continues working even if Flask unavailable
- **Status reporting**: Clear status messages to MCP clients about Flask availability

#### Logging & Monitoring
- **Structured logging**: JSON logs with process lifecycle events
- **Metrics tracking**: Startup times, health check results, restart counts
- **Error aggregation**: Collect and report common failure patterns
- **Debug information**: Detailed logging for troubleshooting

### 5. Configuration Management

#### Shared Configuration Schema
```json
{
  "flask": {
    "port": 5000,
    "debug": false,
    "host": "127.0.0.1"
  },
  "mcp": {
    "health_check_interval": 30,
    "restart_threshold": 3,
    "shutdown_timeout": 10
  },
  "logging": {
    "level": "INFO",
    "format": "json"
  }
}
```

#### Environment Variables
- `PROMPTBIN_MODE`: `mcp-managed` or `standalone`
- `PROMPTBIN_PORT`: Flask application port
- `PROMPTBIN_DATA_DIR`: Directory for prompt storage
- `PROMPTBIN_LOG_LEVEL`: Logging verbosity

## Deliverables
1. `FlaskManager` class with complete subprocess management
2. Health check system with HTTP endpoints and process monitoring  
3. Configuration management system shared between MCP and Flask
4. Robust error handling and recovery mechanisms
5. Port management and conflict resolution
6. Graceful shutdown procedures with resource cleanup
7. Comprehensive logging and monitoring

## Testing Requirements
- Test Flask startup and shutdown sequences
- Verify health checks work correctly
- Test automatic restart on Flask crashes
- Validate port conflict handling
- Test graceful shutdown with active requests
- Verify no zombie processes or resource leaks
- Test configuration sharing between processes

## Success Criteria
- MCP server successfully launches Flask app on startup
- Health monitoring detects and recovers from Flask failures
- Graceful shutdown leaves no orphaned processes
- Port conflicts are handled automatically
- Configuration is properly shared between processes
- Error recovery works reliably under various failure conditions
- Both processes can run independently or together

## Notes
- Use `asyncio` for non-blocking subprocess management if MCP server is async
- Consider using process pools for improved reliability
- Document the complete lifecycle for debugging purposes
- Test extensively with simulated failures and resource constraints
- Ensure compatibility with different operating systems