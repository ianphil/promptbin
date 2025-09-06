# Prompt 4: Implement Split-Pane Editor

Create a split-pane editor interface for prompt creation/editing:

1. Left pane: Plain textarea for prompt input
2. Right pane: Live syntax-highlighted preview
3. Support template variables with {{variable}} syntax - highlight these specially
4. Metadata fields above editor: title, category dropdown, description, tags (comma-separated)
5. Live preview updates via HTMX as user types (with debounce)
6. Responsive layout that stacks panes on mobile
7. Action buttons: Save, Cancel, and (on edit) Delete with confirmation

The preview should use highlight.js to format the prompt content and specially highlight {{template_variables}}.