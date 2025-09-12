# UI Redesign Command

Creates 3 worktrees and deploys parallel UI design agents to create distinct UI variants for PromptBin.

## Command

```
/ui-redesign
```

## Prompt

I need you to create 3 different UI redesigns for PromptBin using parallel subagents in separate worktrees.

**Step 1: Create 3 worktrees with new branches**
```bash
git checkout -b ui-variant-modern
git checkout -b ui-variant-creative  
git checkout -b ui-variant-minimal
git checkout master
git worktree add ../promptbin-ui-modern ui-variant-modern
git worktree add ../promptbin-ui-creative ui-variant-creative
git worktree add ../promptbin-ui-minimal ui-variant-minimal
```

**Step 2: Launch 3 parallel UI design architect agents**

Launch all 3 agents in parallel using the Task tool with subagent_type "ui-design-architect":

**Agent 1 - Modern Professional UI:**
Working directory: `/home/cip/src/promptbin-ui-modern` (ui-variant-modern branch)
Task: Create a modern, professional UI redesign for PromptBin - a Model Context Protocol (MCP) server with prompt management capabilities.

Key requirements:
- PromptBin is a Flask web app using HTMX for dynamic interactions
- Current UI is basic HTML templates - needs complete modernization  
- Focus on clean, professional design with excellent UX
- Template variables use {{variable}} syntax with special highlighting
- Categories: coding, writing, analysis
- Key features: create/edit prompts, organize by category, search, share functionality
- Must maintain HTMX compatibility (no full page reloads)

Current structure:
- Templates in `src/promptbin/web/templates/`
- Static files in `src/promptbin/web/static/`
- Main routes: /, /create, /edit/<id>, /category/<name>, /search, /share

Goal: Create a modern, clean, and highly usable interface that makes prompt management intuitive and efficient. Focus on UI/UX excellence with a professional appearance. Use glassmorphism, modern typography (Inter font), card-based layouts, and professional color schemes.

CRITICAL: You are working in `/home/cip/src/promptbin-ui-modern`. All file paths must be relative to this directory. Do not work in any other directory.

**Agent 2 - Creative/Artistic UI:**
Working directory: `/home/cip/src/promptbin-ui-creative` (ui-variant-creative branch)  
Task: Create a creative, visually striking UI redesign for PromptBin - a Model Context Protocol (MCP) server with prompt management capabilities.

Key requirements:
- PromptBin is a Flask web app using HTMX for dynamic interactions
- Current UI is basic HTML templates - needs complete creative overhaul
- Focus on innovative design, visual appeal, and engaging user experience
- Template variables use {{variable}} syntax with special highlighting
- Categories: coding, writing, analysis  
- Key features: create/edit prompts, organize by category, search, share functionality
- Must maintain HTMX compatibility (no full page reloads)

Current structure:
- Templates in `src/promptbin/web/templates/`
- Static files in `src/promptbin/web/static/`
- Main routes: /, /create, /edit/<id>, /category/<name>, /search, /share

Goal: Create a bold, creative, and visually stunning interface that makes prompt management feel engaging and delightful. Think "Neon Lab" theme with dark backgrounds, neon accents (cyan, magenta, yellow), animated effects, creative typography, and laboratory/experimental metaphors.

CRITICAL: You are working in `/home/cip/src/promptbin-ui-creative`. All file paths must be relative to this directory. Do not work in any other directory.

**Agent 3 - Minimal/Clean UI:**
Working directory: `/home/cip/src/promptbin-ui-minimal` (ui-variant-minimal branch)
Task: Create a minimal, clean UI redesign for PromptBin - a Model Context Protocol (MCP) server with prompt management capabilities.

Key requirements:
- PromptBin is a Flask web app using HTMX for dynamic interactions
- Current UI is basic HTML templates - needs minimalist redesign
- Focus on simplicity, clarity, and functional elegance
- Template variables use {{variable}} syntax with special highlighting
- Categories: coding, writing, analysis
- Key features: create/edit prompts, organize by category, search, share functionality
- Must maintain HTMX compatibility (no full page reloads)

Current structure:
- Templates in `src/promptbin/web/templates/`
- Static files in `src/promptbin/web/static/`
- Main routes: /, /create, /edit/<id>, /category/<name>, /search, /share

Goal: Create a clean, minimal, and highly functional interface that emphasizes content over decoration. Think clean lines, generous whitespace, excellent typography, and intuitive navigation. Use system fonts and a grayscale palette with subtle blue accents.

CRITICAL: You are working in `/home/cip/src/promptbin-ui-minimal`. All file paths must be relative to this directory. Do not work in any other directory.

**Step 3: Verify results**
After all agents complete, check each worktree for file changes:
```bash
cd ../promptbin-ui-modern && git status
cd ../promptbin-ui-creative && git status  
cd ../promptbin-ui-minimal && git status
```

**Step 4: Provide viewing instructions**
Give commands to run each variant on different ports:
```bash
# Modern Professional UI
cd ../promptbin-ui-modern && uv run promptbin --web --port 5001

# Creative/Artistic UI  
cd ../promptbin-ui-creative && uv run promptbin --web --port 5002

# Minimal/Clean UI
cd ../promptbin-ui-minimal && uv run promptbin --web --port 5003
```

## Expected Outcome

3 distinct UI variants:
1. **Modern Professional** - Glassmorphism, Inter font, professional colors
2. **Creative/Artistic** - Neon Lab theme, dark mode, animated effects  
3. **Minimal/Clean** - System fonts, whitespace, grayscale with blue accents

Each variant should maintain full HTMX functionality while providing completely different visual experiences.