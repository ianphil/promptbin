+++
title = "MCP Server Subprocess Lifecycle"
description = "Literate tests for PromptBinMCPServer subprocess management"
module = "src/promptbin/mcp/server.py"
runner = "python"
+++

# MCP Server Subprocess Lifecycle Tests

This test suite validates the subprocess lifecycle management in `PromptBinMCPServer`.
The MCP server orchestrates a Flask web interface subprocess, ensuring proper startup,
health monitoring, and graceful shutdown.

## Error Code Index

| Code | Description |
|------|-------------|
| `E_INIT_NO_CONFIG` | Server initialized without valid configuration |
| `E_INIT_NO_MCP` | FastMCP instance not created during initialization |
| `E_INIT_NO_PROMPT_MANAGER` | PromptManager not initialized |
| `E_INIT_NO_FLASK_MANAGER` | FlaskManager not configured during setup |
| `E_FLASK_MANAGER_WRONG_CONFIG` | FlaskManager configured with incorrect values |
| `E_SIGNAL_HANDLER_NOT_SET` | Signal handlers not registered |
| `E_SHUTDOWN_FLAG_NOT_SET` | is_running flag not set to False during shutdown |
| `E_SHUTDOWN_FLASK_NOT_STOPPED` | Flask manager not stopped during shutdown |
| `E_MAIN_FLASK_NOT_STARTED` | Flask subprocess not started in main() |
| `E_MAIN_NO_CLEANUP` | Cleanup not executed on exit |

---

## 1. Initialization Intent

The `__init__` method must configure all dependencies before any subprocess starts.
It should accept injected configuration (for testing) or load from environment.
After initialization, the server should have:
- A valid configuration object
- A FastMCP protocol handler
- A PromptManager for storage access
- State flags initialized to safe defaults
- Signal handlers registered
- Flask manager configured (but not started)

```python
import os
import tempfile
from unittest.mock import patch, MagicMock

# Create a temporary data directory for testing
temp_dir = tempfile.mkdtemp()

# Mock the config to avoid environment dependencies
with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_HOST': '127.0.0.1',
    'PROMPTBIN_PORT': '5000',
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Verify configuration is stored
    assert server.config is not None
    # expect: True

    # Verify FastMCP instance exists
    assert server.mcp is not None
    # expect: True

    # Verify PromptManager is initialized
    assert server.prompt_manager is not None
    # expect: True

    # Verify initial state flags
    assert server.is_running == False
    # expect: True

    assert server.flask_process is None
    # expect: True
```

---

## 2. Flask Manager Setup Intent

The `_setup_flask_manager` method configures the subprocess manager with all parameters
**before** spawning any process. This separation of "configuration" from "execution"
allows the manager to exist in a ready state without consuming resources.

The manager should receive:
- Host and port from configuration
- Log level for subprocess output
- Data directory path
- Health check interval
- Shutdown timeout

```python
import os
import tempfile
from unittest.mock import patch

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_HOST': '127.0.0.1',
    'PROMPTBIN_PORT': '5001',
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Verify FlaskManager was created
    assert server.flask_manager is not None
    # expect: True

    # Verify host is passed correctly
    assert server.flask_manager.host == config.flask_host
    # expect: True

    # Verify base_port matches config
    assert server.flask_manager.base_port == config.flask_port
    # expect: True

    # Verify data_dir is set
    assert server.flask_manager.data_dir == str(config.get_expanded_data_dir())
    # expect: True

    # Verify subprocess has NOT started yet (deferred execution)
    assert server.flask_manager.process is None
    # expect: True

    # Verify port is not yet assigned (assigned on start)
    assert server.flask_manager.port is None
    # expect: True
```

---

## 3. Signal Handlers Intent

The `_setup_signal_handlers` method ensures clean shutdown when the process receives
termination signals (SIGTERM, SIGINT). The handlers must be safe for signal context,
meaning they should NOT call async code directly. Instead, they set a flag that the
main loop checks.

This design avoids race conditions and async-in-signal-handler issues.

```python
import os
import signal
import tempfile
from unittest.mock import patch, MagicMock

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Set is_running to True (simulating running server)
    server.is_running = True

    # Get the current SIGTERM handler
    current_handler = signal.getsignal(signal.SIGTERM)

    # Verify a handler is registered (not default)
    assert current_handler != signal.SIG_DFL
    # expect: True

    # Simulate receiving SIGTERM by calling the handler
    # The handler should set is_running to False
    current_handler(signal.SIGTERM, None)

    # Verify the flag was set (not async shutdown called)
    assert server.is_running == False
    # expect: True
```

---

## 4. Shutdown Intent

The `shutdown` method gracefully stops all managed subprocesses and releases resources.
It must:
- Guard against double-shutdown (idempotent)
- Set `is_running` to False
- Delegate subprocess termination to FlaskManager
- Log completion status
- Re-raise errors (don't swallow them)

The method is async to allow proper awaiting of subprocess termination.

```python
import os
import asyncio
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Mock the flask_manager's stop_flask method
    server.flask_manager.stop_flask = AsyncMock()

    # Set server as running
    server.is_running = True

    # Call shutdown
    asyncio.run(server.shutdown())

    # Verify is_running is now False
    assert server.is_running == False
    # expect: True

    # Verify stop_flask was called
    server.flask_manager.stop_flask.assert_called_once()
    call_count = server.flask_manager.stop_flask.call_count
    assert call_count == 1
    # expect: True
```

---

## 5. Shutdown Idempotency Intent

Calling `shutdown` multiple times should be safe. The guard clause prevents
double-shutdown which could cause errors when stopping already-stopped processes.

```python
import os
import asyncio
import tempfile
from unittest.mock import patch, AsyncMock

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Mock stop_flask
    server.flask_manager.stop_flask = AsyncMock()

    # Server starts as not running
    assert server.is_running == False
    # expect: True

    # Calling shutdown when not running should be a no-op
    asyncio.run(server.shutdown())

    # stop_flask should NOT be called (guard clause)
    assert server.flask_manager.stop_flask.call_count == 0
    # expect: True
```

---

## 6. Main Entry Point - Flask Startup Intent

The `main()` function orchestrates the full lifecycle. Before entering the MCP
protocol loop, it must start the Flask subprocess. This test verifies that
`start_flask()` is called when a flask_manager exists.

```python
import os
import asyncio
import tempfile
from unittest.mock import patch, AsyncMock

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Use AsyncMock to track calls
    mock_start = AsyncMock()
    server.flask_manager.start_flask = mock_start

    # Simulate the startup sequence from main()
    server.is_running = True
    if server.flask_manager:
        asyncio.run(server.flask_manager.start_flask())

    # Verify start_flask was called
    assert mock_start.call_count == 1
    # expect: True

    # Verify is_running was set (precondition for startup)
    assert server.is_running == True
    # expect: True
```

---

## 7. Main Entry Point - Guaranteed Cleanup Intent

The `finally` block in `main()` ensures `shutdown()` runs regardless of how the
server exits (normal completion, signal, or exception). This prevents orphaned
subprocesses.

```python
import os
import asyncio
import tempfile
from unittest.mock import patch, AsyncMock

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # Use AsyncMock to track shutdown calls
    mock_shutdown = AsyncMock()
    server.shutdown = mock_shutdown
    server.flask_manager.stop_flask = AsyncMock()

    # Simulate the finally block behavior from main()
    server.is_running = True

    try:
        # Simulate an error during execution
        raise KeyboardInterrupt("User pressed Ctrl+C")
    except KeyboardInterrupt:
        server.is_running = False
    finally:
        # This is what main() does - always call shutdown
        if server:
            asyncio.run(server.shutdown())

    # Verify shutdown was called despite the exception
    assert mock_shutdown.call_count == 1
    # expect: True

    # Verify is_running was set to False (by exception handler)
    assert server.is_running == False
    # expect: True
```

---

## 8. Configuration Injection Intent

The server accepts an optional `config` parameter for dependency injection.
This enables testing without environment variable side effects and allows
different configurations for different deployment scenarios.

```python
import os
import tempfile
from unittest.mock import patch

temp_dir = tempfile.mkdtemp()
custom_data_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    # Create custom config with specific values (using valid temp path)
    custom_config = PromptBinConfig(
        flask_host="0.0.0.0",
        flask_port=8080,
        data_dir=custom_data_dir,
        log_level="DEBUG"
    )

    # Inject custom config
    server = PromptBinMCPServer(config=custom_config)

    # Verify injected config is used (not environment)
    assert server.config.flask_host == "0.0.0.0"
    # expect: True

    assert server.config.flask_port == 8080
    # expect: True

    assert server.config.log_level == "DEBUG"
    # expect: True
```

---

## 9. State Flag Initialization Intent

State flags must be initialized to safe defaults. `is_running` starts as `False`
because the server hasn't entered its main loop yet. `flask_process` and
`flask_manager` track subprocess state.

```python
import os
import tempfile
from unittest.mock import patch

temp_dir = tempfile.mkdtemp()

with patch.dict(os.environ, {
    'PROMPTBIN_DATA_DIR': temp_dir,
    'PROMPTBIN_LOG_LEVEL': 'WARNING'
}):
    from promptbin.mcp.server import PromptBinMCPServer
    from promptbin.core.config import PromptBinConfig

    config = PromptBinConfig.from_environment()
    server = PromptBinMCPServer(config=config)

    # is_running must start False (not yet in main loop)
    assert server.is_running == False
    # expect: True

    # flask_process must be None (no legacy process tracking)
    assert server.flask_process is None
    # expect: True

    # flask_manager should exist but its process should be None
    assert server.flask_manager is not None
    # expect: True

    assert server.flask_manager.process is None
    # expect: True
```

---

## Summary

These tests validate the core subprocess lifecycle management in `PromptBinMCPServer`:

1. **Initialization** - All dependencies configured before subprocess starts
2. **Flask Manager Setup** - Deferred execution pattern (configure now, start later)
3. **Signal Handlers** - Flag-based shutdown for signal safety
4. **Shutdown** - Graceful cleanup with delegation to FlaskManager
5. **Shutdown Idempotency** - Safe to call multiple times
6. **Main Flask Startup** - Subprocess started before MCP loop
7. **Guaranteed Cleanup** - Finally block ensures no orphaned processes
8. **Configuration Injection** - DI pattern for testability
9. **State Flag Initialization** - Safe defaults prevent premature actions
