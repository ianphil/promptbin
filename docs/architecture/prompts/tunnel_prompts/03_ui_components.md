# Prompt 3: Create Frontend UI Components

Add Dev Tunnels UI components to existing templates:

## Header Status Indicator (`templates/base.html`)

Update the `.tunnel-status` div in header:
- Show tunnel state: "Tunnel: Active" or "Tunnel: Inactive"
- Display tunnel URL when active with copy button
- Use visual indicators (green/red status dot)
- Update status via JavaScript polling or WebSocket

## Footer Controls (`templates/base.html`)

Update the `.tunnel-controls` div in footer:
- "Start Tunnel" button (when inactive)
- "Stop Tunnel" button (when active) 
- Tunnel URL display with copy functionality
- Loading states during operations
- Error message display area

## JavaScript Integration

Add to `base.html` script section:
- `startTunnel()` function with loading feedback
- `stopTunnel()` function with confirmation
- `updateTunnelStatus()` for periodic status checks
- `copyTunnelUrl()` for clipboard operations
- Error handling with user notifications

## Update Share Functions

Modify existing `sharePrompt()` function:
- Use tunnel URL when active instead of localhost
- Show different messaging for tunnel vs local sharing
- Handle tunnel URL in clipboard operations

## Visual Design

- Match existing PromptBin UI/UX patterns
- Use consistent color scheme and typography  
- Add hover states and loading spinners
- Responsive design for mobile devices