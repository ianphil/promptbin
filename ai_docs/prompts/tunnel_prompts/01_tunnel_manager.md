# Prompt 1: Create Dev Tunnel Manager

Create `tunnel_manager.py` with comprehensive Microsoft Dev Tunnels management:

## Core Requirements

1. **TunnelManager Class** with subprocess management for `devtunnel` CLI
2. **Lifecycle Management**: start_tunnel(), stop_tunnel(), get_status(), get_tunnel_url()
3. **Process Handling**: Spawn devtunnel process with proper cleanup on shutdown
4. **URL Parsing**: Extract tunnel URL from devtunnel CLI output
5. **Error Handling**: Graceful failure handling with detailed error messages
6. **Rate Limiting**: Track IP access attempts at application level, auto-shutdown tunnel on abuse
7. **CLI Detection**: Check if devtunnel CLI is installed and user is authenticated

## Implementation Details

- Use subprocess.Popen for process management
- Parse tunnel URL from stdout: `https://tunnel_id-port.region.devtunnels.ms/` (handle real format)
- Store tunnel process PID for cleanup
- Implement context manager for automatic cleanup
- Add logging for tunnel operations
- Check authentication with `devtunnel user show` before operations
- Support both temporary and persistent tunnel modes
- Use correct command: `devtunnel host --port-numbers <port> --allow-anonymous`

## Security Features

- Anonymous access enabled (`--allow-anonymous`) for sharing
- Application-level rate limiting with automatic tunnel termination
- Process cleanup on app shutdown/crash (SIGINT/SIGTERM handling)
- Authentication validation before tunnel operations

The tunnel manager should only expose the Flask app port, not provide full system access.