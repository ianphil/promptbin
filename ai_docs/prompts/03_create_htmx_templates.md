# Prompt 3: Create HTMX-Powered Templates

Create the HTML templates for PromptBin with HTMX integration:

1. base.html: Include HTMX script, highlight.js for syntax highlighting, basic layout with header/sidebar/main/footer
2. index.html: Browse prompts with live search (hx-trigger="keyup changed delay:300ms"), category filtering
3. create.html: Split-pane editor with plain text input on left, live preview on right using hx-post for preview updates
4. view.html: Display single prompt with syntax highlighting, copy button, share controls
5. edit.html: Similar to create but pre-populated with existing prompt data
6. partials/ directory with reusable HTMX fragments for prompt cards, search results, preview pane

Use hx-push-url="true" for navigation to maintain browser history without full reloads.