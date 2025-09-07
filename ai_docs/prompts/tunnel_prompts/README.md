# Dev Tunnels Implementation Prompts

This directory contains implementation prompts for Microsoft Dev Tunnels integration in PromptBin.

## Implementation Order

Execute these prompts in sequence for systematic implementation:

1. **[01_tunnel_manager.md](01_tunnel_manager.md)** - Core tunnel management class
2. **[02_backend_api.md](02_backend_api.md)** - Flask API endpoints  
3. **[03_ui_components.md](03_ui_components.md)** - Frontend UI components
4. **[04_security_implementation.md](04_security_implementation.md)** - Security features
5. **[05_installation_setup.md](05_installation_setup.md)** - Installation & documentation

## Overview

These prompts implement the Dev Tunnels integration plan from `08a_dev_tunnels_plan.md` with:

- Secure tunnel management with subprocess handling
- UI controls for start/stop tunnel operations  
- Rate limiting protection (5 attempts per IP)
- Anonymous access configuration for sharing
- Cross-platform devtunnel CLI integration
- Comprehensive error handling and security

## Prerequisites

- Microsoft Dev Tunnels CLI installed (`devtunnel --version` to verify)
- Authentication with Microsoft or GitHub account (`devtunnel user show` to check)
- Flask app running on localhost (port 5000 or 5001)

## Security Notes

The tunnel implementation:
- Only exposes the Flask app, not full system access
- Implements application-level rate limiting with automatic shutdown
- Requires explicit user action to start tunnels
- Uses temporary tunnels (deleted on stop)
- Includes authentication validation and proper error handling