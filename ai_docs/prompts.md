# PromptBin Development Prompts

## Project Setup & Core Structure

### Prompt 1: Initialize Project Structure
```
Create the initial project structure for PromptBin, a local-first prompt management tool. Set up:
1. A Python project with Flask as the web framework
2. File-based storage structure in a prompts/ directory with subdirectories for coding/, writing/, and analysis/
3. Basic Flask app.py with routes for index, create, view, edit operations
4. Templates directory with base.html using HTMX
5. A requirements.txt with Flask, and other necessary dependencies
6. Basic CSS file in static/css/style.css

The app should run on localhost:5000 and use HTMX for dynamic interactions without full page reloads.
```

### Prompt 2: Implement File-Based Storage System
```
Implement a file-based storage system for PromptBin that:
1. Stores prompts as JSON files in the prompts/ directory structure
2. Each prompt file contains: id, title, content, category, description, tags, created_at, updated_at
3. Creates a PromptManager class with methods: save_prompt(), get_prompt(), list_prompts(), delete_prompt(), search_prompts()
4. Handles file operations with proper error handling
5. Generates unique IDs for prompts using timestamps and random strings
6. Supports moving prompts between categories

Store files as: prompts/{category}/{prompt_id}.json
```

## Web Interface Development

### Prompt 3: Create HTMX-Powered Templates
```
Create the HTML templates for PromptBin with HTMX integration:

1. base.html: Include HTMX script, highlight.js for syntax highlighting, basic layout with header/sidebar/main/footer
2. index.html: Browse prompts with live search (hx-trigger="keyup changed delay:300ms"), category filtering
3. create.html: Split-pane editor with plain text input on left, live preview on right using hx-post for preview updates
4. view.html: Display single prompt with syntax highlighting, copy button, share controls
5. edit.html: Similar to create but pre-populated with existing prompt data
6. partials/ directory with reusable HTMX fragments for prompt cards, search results, preview pane

Use hx-push-url="true" for navigation to maintain browser history without full reloads.
```

### Prompt 4: Implement Split-Pane Editor
```
Create a split-pane editor interface for prompt creation/editing:

1. Left pane: Plain textarea for prompt input
2. Right pane: Live syntax-highlighted preview
3. Support template variables with {{variable}} syntax - highlight these specially
4. Metadata fields above editor: title, category dropdown, description, tags (comma-separated)
5. Live preview updates via HTMX as user types (with debounce)
6. Responsive layout that stacks panes on mobile
7. Action buttons: Save, Cancel, and (on edit) Delete with confirmation

The preview should use highlight.js to format the prompt content and specially highlight {{template_variables}}.
```

### Prompt 5: Add Search and Navigation
```
Implement search and navigation features:

1. Live search bar in header that searches prompt titles, content, and tags
2. HTMX-powered search with results updating without page reload
3. Category sidebar navigation showing prompt counts per category
4. Click on category filters the prompt list
5. Search results show highlighted matching text
6. "Clear filters" button to reset view
7. Pagination or infinite scroll for large prompt lists (using HTMX)

Search should be case-insensitive and support partial matches.
```

## MCP Server Integration

### Prompt 6: Create MCP Server Component
```
Create mcp_server.py that implements the Model Context Protocol:

1. MCP server that can be loaded by AI tools like Claude
2. On startup, automatically launches the Flask web app as a subprocess
3. Implements MCP endpoints: list_prompts(), get_prompt(prompt_id), search_prompts(query)
4. Handles graceful shutdown - when MCP server stops, it cleanly terminates the Flask subprocess
5. Provides prompt access via protocol: mcp://promptbin/get-prompt/{prompt-name}
6. Include proper error handling and logging

The MCP server should monitor the Flask subprocess and restart it if it crashes unexpectedly.
```

### Prompt 7: Implement Auto-Lifecycle Management
```
Enhance the MCP server with robust lifecycle management:

1. MCP server starts Flask app on initialization with proper process management
2. Health checks to ensure Flask is running and responsive
3. Automatic restart of Flask if it becomes unresponsive
4. Clean shutdown sequence that ensures no orphaned processes
5. Standalone mode: app.py can also run independently without MCP server
6. Environment detection to know if running under MCP or standalone
7. Shared configuration between MCP server and Flask app

Add status endpoints to check if running in MCP mode or standalone mode.
```

## Sharing & Security Features

### Prompt 8: Integrate Microsoft Dev Tunnels
```
Add Microsoft Dev Tunnels integration for secure sharing:

1. Add tunnel management to Flask app with start/stop controls
2. UI button to "Start Tunnel" that spawns devtunnel process
3. Parse tunnel URL from devtunnel output and store in app state
4. Update all "Copy URL" buttons to use tunnel URL when active
5. Show tunnel status indicator in header (active/inactive with URL)
6. "Stop Tunnel" button that kills the tunnel process
7. Handle tunnel process errors gracefully

The tunnel should only expose the Flask app, not give full system access.
```

### Prompt 9: Implement Share Token System
```
Create a secure sharing system with access tokens:

1. Generate cryptographically secure tokens for shared prompts
2. Share URLs format: /share/<token>/<prompt_id>
3. Token validation middleware that checks token before serving prompt
4. Store active tokens in memory (reset on app restart)
5. Public share view that shows prompt read-only with limited UI
6. Origin validation - only /share/ routes accessible via tunnel
7. Regular routes return 403 when accessed from tunnel URL

Include a "Generate Share Link" button that creates token and shows copyable URL.
```

### Prompt 10: Add Security & Rate Limiting
```
Implement security features for shared prompts:

1. Rate limiting: Track failed access attempts per IP
2. After 5 failed attempts from an IP, automatically kill tunnel
3. Show security alerts in UI when suspicious activity detected
4. Log all external access attempts with timestamps and IPs
5. Implement CSRF protection for all state-changing operations
6. Add request origin validation to prevent unauthorized tunnel access
7. Security dashboard showing recent access attempts and blocked IPs

The rate limiter should reset counts after successful access or manual reset.
```

## Polish & Advanced Features

### Prompt 11: Enhanced Syntax Highlighting
```
Improve syntax highlighting and template support:

1. Configure highlight.js for markdown and code block detection
2. Special highlighting for {{template_variables}} with different color
3. Support nested code blocks with language detection
4. Line numbers option for code blocks
5. Copy button for individual code blocks
6. Template variable validation - highlight invalid/unclosed variables
7. Preview pane should closely match how prompts appear in AI tools

Add a template variable sidebar that lists all detected variables in the prompt.
```

### Prompt 12: Import/Export & Backup
```
Add import/export functionality:

1. Export all prompts as ZIP file with preserved directory structure
2. Export single prompt as JSON or Markdown
3. Import prompts from ZIP maintaining categories
4. Import validation to prevent overwriting without confirmation
5. Automatic backup system that creates timestamped backups
6. Version history by keeping old versions when prompts are edited
7. Bulk operations: delete multiple, move to category, export selected

Include progress indicators for bulk operations using HTMX.
```

### Prompt 13: Usage Analytics & Metadata
```
Add analytics and enhanced metadata:

1. Track prompt usage: times accessed via MCP, times shared, times copied
2. Last accessed timestamp for each prompt
3. Popular prompts dashboard showing most used
4. Search history to show recent searches
5. Tag cloud showing all tags with size based on frequency
6. Prompt statistics: total prompts, by category, average length
7. Activity feed showing recent creates/edits/shares

Store analytics data in a separate analytics/ directory to keep it isolated.
```

### Prompt 14: UI Polish & Responsive Design
```
Polish the user interface for professional appearance:

1. Modern, clean design with consistent spacing and typography
2. Dark mode toggle with CSS variables for theming
3. Responsive design that works on mobile/tablet/desktop
4. Loading states for all HTMX operations
5. Toast notifications for actions (saved, copied, deleted)
6. Keyboard shortcuts (Ctrl+S save, Ctrl+K search, etc.)
7. Smooth transitions and micro-animations for better UX

Include empty states with helpful messages when no prompts exist.
```

### Prompt 15: Testing & Documentation
```
Create comprehensive testing and documentation:

1. Unit tests for PromptManager and file operations
2. Integration tests for Flask routes
3. MCP server tests including lifecycle management
4. Security tests for rate limiting and token validation
5. README.md with installation, usage, and MCP configuration instructions
6. API documentation for MCP protocol endpoints
7. Troubleshooting guide for common issues
8. Example prompts to seed the initial installation

Include GitHub Actions workflow for automated testing.
```

## Deployment & Distribution

### Prompt 16: Package for Distribution
```
Prepare PromptBin for distribution:

1. Create setup.py for pip installation
2. Configure package to work with uv package manager
3. Bundle all dependencies with version pinning
4. Create promptbin CLI command that starts the app
5. Add --standalone and --mcp flags for different modes
6. Include man page or help documentation
7. Create install script that sets up initial directory structure
8. Add to PyPI for easy installation: uv add promptbin

Ensure cross-platform compatibility (Windows, macOS, Linux).
```

## Usage Instructions

These prompts should be used sequentially to build PromptBin. Each prompt builds upon the previous ones:

1. Start with prompts 1-2 to create the foundation
2. Build the web interface with prompts 3-5
3. Add MCP integration with prompts 6-7
4. Implement sharing features with prompts 8-10
5. Polish and enhance with prompts 11-14
6. Finish with testing and deployment (prompts 15-16)

Each prompt is self-contained enough to be understood independently but assumes previous prompts have been completed when building the full application.

## Tips for Using These Prompts

- You can combine related prompts if working with an AI with larger context
- Test each component thoroughly before moving to the next
- Consider security implications at each step
- Keep the local-first philosophy central to all decisions
- Ensure HTMX interactions provide smooth UX without full page loads
- Test MCP integration with actual AI tools during development
- Document any deviations from the PRD as you build
