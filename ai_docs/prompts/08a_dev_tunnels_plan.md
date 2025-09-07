# Microsoft Dev Tunnels Integration Plan

## Overview
Integrate Microsoft Dev Tunnels for secure sharing of the PromptBin Flask app, with UI controls and automatic security protections based on `ai_docs/prompts/08_integrate_dev_tunnels.md`.

## Implementation Steps

### 1. Create Dev Tunnel Manager (`tunnel_manager.py`)
- Add subprocess management for `devtunnel` CLI
- Implement tunnel lifecycle (start/stop/status checking)
- Parse tunnel URL from devtunnel output
- Handle authentication requirements
- Implement error handling and process cleanup
- Add rate limiting protection (5 attempts per IP kills tunnel)

### 2. Backend API Endpoints (`app.py`)
- Add `/api/tunnel/start` endpoint to spawn devtunnel process
- Add `/api/tunnel/stop` endpoint to kill tunnel process
- Add `/api/tunnel/status` endpoint for current tunnel state
- Add `/api/tunnel/url` endpoint to get active tunnel URL
- Update share URL generation to use tunnel URL when active
- Integrate rate limiting middleware

### 3. Frontend UI Components
- Add tunnel status indicator in header (active/inactive with URL)
- Add "Start Tunnel" button in footer/controls area
- Add "Stop Tunnel" button when tunnel is active
- Update "Copy URL" buttons to use tunnel URL when active
- Add tunnel URL display with copy functionality
- Add visual feedback for tunnel operations

### 4. Security Implementation
- Install devtunnel CLI check on startup
- Anonymous access configuration (`--allow-anonymous`)
- IP-based rate limiting (5 attempts triggers tunnel shutdown)
- Origin validation for tunnel requests
- Graceful error handling for tunnel failures

### 5. Installation & Dependencies
- Add devtunnel CLI installation instructions
- Update requirements for subprocess management
- Add system compatibility checks (Linux support via curl install)
- Document authentication requirements (Microsoft/GitHub account)

## Technical Details

### Dev Tunnel Configuration
- Port: 5000 (Flask default) or 5001 (current app default)
- Protocol: HTTP (as specified in docs for localhost)
- Access: Anonymous (required for sharing)
- Persistence: Temporary tunnels (deleted on stop)

### Security Architecture
- Private by default (localhost only)
- Explicit tunnel activation required
- Automatic shutdown on rate limit breach
- Process cleanup on app shutdown

### UI/UX Features
- Real-time tunnel status updates
- One-click tunnel URL copying
- Clear visual indicators for tunnel state
- Error notifications for tunnel failures