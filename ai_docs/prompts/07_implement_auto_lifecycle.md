# Prompt 7: Implement Auto-Lifecycle Management

Enhance the MCP server with robust lifecycle management:

1. MCP server starts Flask app on initialization with proper process management
2. Health checks to ensure Flask is running and responsive
3. Automatic restart of Flask if it becomes unresponsive
4. Clean shutdown sequence that ensures no orphaned processes
5. Standalone mode: app.py can also run independently without MCP server
6. Environment detection to know if running under MCP or standalone
7. Shared configuration between MCP server and Flask app

Add status endpoints to check if running in MCP mode or standalone mode.