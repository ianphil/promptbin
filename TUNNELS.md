# Microsoft Dev Tunnels Integration Guide

This document provides comprehensive technical information about PromptBin's Microsoft Dev Tunnels integration for secure public sharing.

## What are Microsoft Dev Tunnels?

Microsoft Dev Tunnels is a service that creates secure HTTP/HTTPS tunnels from the public internet to your local development server. Think of it as a secure, temporary way to make your local PromptBin instance accessible from anywhere on the internet.

### How It Works

1. **Local Server**: Your PromptBin runs locally (e.g., `localhost:5001`)
2. **Tunnel Creation**: Dev Tunnels creates a public URL (e.g., `https://abc123-5001.use2.devtunnels.ms`)  
3. **Traffic Forwarding**: Requests to the public URL are securely forwarded to your local server
4. **Anonymous Access**: Share URLs work without requiring authentication from visitors

### Key Benefits

- **No Port Forwarding**: No need to configure routers or firewalls
- **HTTPS by Default**: All tunnel URLs use secure HTTPS connections
- **Microsoft Infrastructure**: Runs on Microsoft's global network with high availability
- **Authentication Required**: Only you can create tunnels (requires Microsoft/GitHub account)
- **Automatic Cleanup**: Tunnels automatically shut down when your app stops

## Security Model

### Authentication & Authorization

- **Tunnel Creation**: Requires Microsoft account or GitHub authentication
- **Share Access**: Shared prompts are accessible anonymously (by design)
- **Rate Limiting**: Built-in protection against abuse (5 attempts per IP per 30 minutes)
- **Origin Validation**: Microsoft validates tunnel ownership

### Privacy Considerations

**⚠️ Important Privacy Notes:**

- **Public Internet**: Tunnel URLs are accessible from anywhere on the internet
- **Microsoft Routing**: Traffic flows through Microsoft's Dev Tunnels infrastructure
- **Shared Content**: Only explicitly shared prompts are accessible via tunnels
- **Local Data**: Your full prompt library remains private (only shared items are exposed)
- **Temporary URLs**: Share tokens expire and reset on app restart

### Best Practices

1. **Only Share What You Intend**: Review prompts before sharing
2. **Monitor Active Tunnels**: Stop tunnels when not actively sharing
3. **Avoid Sensitive Data**: Don't share prompts containing secrets, API keys, or personal information
4. **Use Rate Limiting**: Let the built-in rate limiting protect against abuse
5. **Regular Cleanup**: Restart the app to reset share tokens periodically

## Technical Implementation

### Rate Limiting System

PromptBin implements application-level rate limiting for tunnel operations:

```
Rate Limit: 5 attempts per IP address per 30-minute window
Actions Covered: Tunnel start requests
Consequences: Automatic tunnel shutdown, temporary IP blocking
Reset: 30-minute sliding window, or app restart
```

### Process Management

- **Subprocess Handling**: Tunnels run as child processes of the Flask app
- **Signal Handling**: Clean shutdown on Ctrl+C or SIGTERM
- **Automatic Cleanup**: `atexit` handlers ensure no orphaned processes
- **Health Monitoring**: Built-in status checking and process monitoring

### URL Integration

When a tunnel is active:
- Share links automatically use tunnel URLs instead of localhost
- Health endpoint includes tunnel status information
- UI shows live tunnel status with copy functionality
- JavaScript automatically updates tunnel state every 30 seconds

## Troubleshooting Guide

### Installation Issues

**Problem**: `devtunnel: command not found`
```bash
# Solution: Install the CLI
curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel
chmod +x devtunnel
sudo mv devtunnel /usr/local/bin/
```

**Problem**: Permission denied during installation
```bash
# Solution: Install to user directory
curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel
chmod +x devtunnel
mkdir -p ~/.local/bin
mv devtunnel ~/.local/bin/
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Authentication Issues

**Problem**: "Not authenticated" error
```bash
# Solution: Login with GitHub (recommended)
devtunnel user login -g

# Or with Microsoft account
devtunnel user login

# Verify authentication
devtunnel user show
```

**Problem**: Authentication expires
```bash
# Solution: Re-authenticate
devtunnel user logout
devtunnel user login -g
```

### Tunnel Operation Issues

**Problem**: "Rate limit exceeded" error
- **Cause**: Too many tunnel start attempts from your IP
- **Solution**: Wait 30 minutes, or restart the PromptBin app to reset counters
- **Prevention**: Use tunnels judiciously, stop when not needed

**Problem**: Tunnel starts but URL is not accessible
- **Check**: Verify the tunnel URL format (`https://id-port.region.devtunnels.ms`)
- **Check**: Ensure your local Flask app is running on the correct port
- **Check**: Test local access first (`curl localhost:5001`)

**Problem**: Tunnel process won't stop
```bash
# Manual cleanup if needed
ps aux | grep devtunnel
kill <process_id>
```

### Network & Connectivity Issues

**Problem**: Tunnel creation times out
- **Cause**: Network connectivity issues
- **Solution**: Check internet connection, try again
- **Alternative**: Use different network or VPN

**Problem**: Slow tunnel performance
- **Cause**: Geographic distance from Microsoft data centers
- **Info**: This is normal - tunnels add network latency
- **Mitigation**: For production use, consider proper hosting

### Application Integration Issues

**Problem**: Share links still use localhost
- **Check**: Ensure tunnel is actually started (check footer status)
- **Check**: Verify tunnel URL is returned by `/api/tunnel/status`
- **Solution**: Refresh the page after starting tunnel

**Problem**: UI shows "Tunnel: Inactive" but tunnel is running
- **Solution**: Check browser developer console for JavaScript errors
- **Solution**: Try refreshing the page or restarting the app

## Advanced Configuration

### Environment Variables

Set these in your shell or `.env` file to customize tunnel behavior:

```bash
# Feature control
DEVTUNNEL_ENABLED=true          # Enable/disable tunnel functionality (default: true)
DEVTUNNEL_AUTO_START=false      # Auto-start tunnel on share (default: false)

# Rate limiting
DEVTUNNEL_RATE_LIMIT=5          # Max attempts per time window (default: 5)
DEVTUNNEL_RATE_WINDOW=30        # Time window in minutes (default: 30)

# Logging
DEVTUNNEL_LOG_LEVEL=info        # Tunnel operation log level: debug, info, warning, error (default: info)

# Example: Disable tunnels entirely
export DEVTUNNEL_ENABLED=false

# Example: Increase rate limit for development
export DEVTUNNEL_RATE_LIMIT=20
export DEVTUNNEL_RATE_WINDOW=5

# Example: Enable detailed logging
export DEVTUNNEL_LOG_LEVEL=debug
```

These environment variables are read when the TunnelManager initializes and control various aspects of tunnel behavior.

### CLI Configuration

You can also configure Dev Tunnels globally:

```bash
# List active tunnels
devtunnel list

# Delete all tunnels (cleanup)
devtunnel delete --all

# View detailed help
devtunnel help
```

## Security Considerations

### Data Flow

```
Internet User → devtunnels.ms → Microsoft Infrastructure → Your Computer → Flask App
```

### What Microsoft Can See

- **Tunnel Metadata**: Creation time, duration, data transfer volumes
- **Request Headers**: Standard HTTP headers (User-Agent, etc.)
- **Not Content**: Microsoft doesn't log or inspect your prompt content
- **Authentication**: Your Microsoft/GitHub identity for tunnel creation

### What's Shared Publicly

- **Only Shared Prompts**: Individual prompts you explicitly share
- **Share URLs**: Temporary URLs with cryptographic tokens
- **Not Your Full Library**: Private prompts remain private
- **Not System Info**: No access to your computer beyond the Flask app

### Compliance Notes

- **Enterprise Use**: Check your organization's policies before using tunnels
- **Data Residency**: Traffic flows through Microsoft's global infrastructure
- **Audit Logs**: Microsoft may retain metadata for service operation
- **Terms of Service**: Subject to Microsoft Dev Tunnels terms and conditions

## Support & Resources

- **Microsoft Docs**: [Azure Dev Tunnels Documentation](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/)
- **GitHub Issues**: Report PromptBin tunnel issues at the project repository
- **CLI Help**: Run `devtunnel help` for built-in documentation
- **Service Status**: Check Microsoft Azure status for Dev Tunnels service health

## Limitations

### Technical Limits
- **Request Size**: Standard HTTP request size limits apply
- **Concurrent Connections**: Limited by Microsoft's service quotas
- **Geographic Regions**: Performance varies by distance to Microsoft data centers
- **Uptime**: Service availability subject to Microsoft's SLA

### Usage Limits
- **Rate Limiting**: 5 tunnel creation attempts per IP per 30 minutes
- **Authentication Required**: Must have Microsoft or GitHub account
- **Single Tunnel**: PromptBin creates one tunnel per instance
- **Manual Management**: Tunnels don't auto-restart after network issues

### Functional Limits
- **HTTP/HTTPS Only**: No support for other protocols
- **Public Access**: Can't restrict tunnel access to specific users
- **No Custom Domains**: Must use Microsoft-provided URLs
- **Session Based**: Share tokens reset when app restarts