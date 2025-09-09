# Prompt 4: Implement Security Features

Add comprehensive security measures for Dev Tunnels integration:

## CLI Installation Check

Add to app startup (`app.py` or new `setup_checks.py`):
- Check if `devtunnel` CLI is installed and accessible
- Verify devtunnel version compatibility  
- Show installation instructions if missing
- Graceful fallback when devtunnel unavailable

## Rate Limiting System

Implement IP-based rate limiting:
- Track IP addresses accessing tunnel endpoints
- Store attempt counters in memory (dict or Redis if available)
- 5-attempt limit per IP address
- Auto-shutdown tunnel when limit exceeded
- Reset counters on tunnel restart or manual reset

## Authentication Handling

Add devtunnel authentication support:
- Use `devtunnel user show` to check authentication status
- Provide login instructions if not authenticated (`devtunnel user login` or `devtunnel user login -g`)
- Handle authentication errors gracefully
- Support both Microsoft and GitHub accounts
- Validate authentication before tunnel operations

## Origin Validation

Add request origin validation:
- Validate requests coming through tunnel
- Block suspicious or malicious requests
- Log security events for monitoring
- Implement basic DDoS protection

## Process Security

Ensure secure process management:
- Run devtunnel with minimal privileges
- Prevent command injection in tunnel parameters
- Secure process cleanup on app shutdown
- Monitor tunnel process health

## Error Handling

Implement comprehensive error handling:
- Network connectivity issues
- CLI authentication failures
- Process startup/shutdown errors
- Rate limit exceeded scenarios
- Tunnel service unavailable