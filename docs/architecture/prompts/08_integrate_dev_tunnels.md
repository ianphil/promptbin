# Prompt 8: Integrate Microsoft Dev Tunnels

Add Microsoft Dev Tunnels integration for secure sharing:

1. Add tunnel management to Flask app with start/stop controls
2. UI button to "Start Tunnel" that spawns devtunnel process
3. Parse tunnel URL from devtunnel output and store in app state
4. Update all "Copy URL" buttons to use tunnel URL when active
5. Show tunnel status indicator in header (active/inactive with URL)
6. "Stop Tunnel" button that kills the tunnel process
7. Handle tunnel process errors gracefully

The tunnel should only expose the Flask app, not give full system access.