# Prompt 6: Create MCP Server Component

Create mcp_server.py that implements the Model Context Protocol:

1. MCP server that can be loaded by AI tools like Claude
2. On startup, automatically launches the Flask web app as a subprocess
3. Implements MCP endpoints: list_prompts(), get_prompt(prompt_id), search_prompts(query)
4. Handles graceful shutdown - when MCP server stops, it cleanly terminates the Flask subprocess
5. Provides prompt access via protocol: mcp://promptbin/get-prompt/{prompt-name}
6. Include proper error handling and logging

The MCP server should monitor the Flask subprocess and restart it if it crashes unexpectedly.