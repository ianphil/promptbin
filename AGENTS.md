# Repository Guidelines

PromptBin is an **MCP server example** designed for easy distribution and usage via PyPI.

**Primary workflow**: `uv add promptbin && uv run promptbin`

## Project Structure & Module Organization
- **src/promptbin/app.py**: Complete Flask web app with all routes, views, and lifecycle management.
- **src/promptbin/mcp/server.py**: Full MCP server implementation with subprocess integration.
- **src/promptbin/managers/prompt_manager.py**: File-based storage with search, categories, and metadata.
- **src/promptbin/managers/share_manager.py**: Secure sharing logic with ephemeral tokens.
- **src/promptbin/managers/tunnel_manager.py**: Microsoft Dev Tunnels integration with rate limiting and security.
- **src/promptbin/utils/setup_checker.py**: System validation and diagnostic tool.
- **src/promptbin/utils/install_devtunnel.py**: Cross-platform installer automation.
- **src/promptbin/web/templates/** and **static/**: HTMX-powered UI templates and assets.
- **~/promptbin-data/**: Local JSON prompt data, organized by category (coding, writing, analysis).
- **TUNNELS.md**: Comprehensive technical documentation for Dev Tunnels.
- **ai_docs/**: Internal planning and development prompts (completed phases).

## Build, Test, and Development Commands

**Production usage** (PyPI):
- **Install**: `uv add promptbin` (requires Python 3.11+ and uv).
- **Run both MCP + web**: `uv run promptbin` (primary use case).
- **Run MCP only**: `uv run promptbin --mcp` (MCP server mode).
- **Run web only**: `uv run promptbin --web` (standalone web mode).
- **Setup verification**: `uv run promptbin-setup` (validates system readiness).
- **Install Dev Tunnels**: `uv run promptbin-install-tunnel` (cross-platform installer).

**Development** (local):
- **Install deps**: `uv sync`.
- **Run both MCP + web**: `uv run promptbin`.
- **Run MCP only**: `uv run promptbin --mcp`.
- **Run web only**: `uv run promptbin --web`.
- **Lint/format**: None enforced; see style section below.

## Coding Style & Naming Conventions
- Python style: PEP 8, 4‑space indents, descriptive names.
- Types: prefer type hints for public functions and return values.
- Modules: keep files focused (web in src/promptbin/app.py, protocol in src/promptbin/mcp/server.py, storage in src/promptbin/managers/prompt_manager.py).
- IDs: prompt files named `<id>.json` under `~/promptbin-data/<category>/` (IDs generated like `YYYYMMDD_HHMMSS_xxxxxxxx`).
- Categories: use one of `coding`, `writing`, `analysis`.

## Testing Guidelines
- **Current status**: No formal test suite yet, but comprehensive manual validation via setup_checker.py.
- **If adding tests**: Use `pytest`; place tests in `tests/` and name files `test_*.py`.
- **Priority areas**: PromptManager (save/get/list/search/delete), share token validation, tunnel rate limiting.
- **Testing tools**: `src/promptbin/utils/setup_checker.py` validates system configuration and readiness.
- **Manual validation**: Run `uv run promptbin-setup` to check all components.
- **Aim for**: Clear, isolated tests over broad integration first.

## Commit & Pull Request Guidelines
- Commits: prefer Conventional Commits (e.g., `feat:`, `fix:`, `chore:`). Keep messages imperative and scoped.
- PRs: include a concise summary, linked issues, screenshots/gifs for UI changes, and repro/validation steps (commands and expected outcomes).
- Keep PRs small and cohesive; note any follow‑ups explicitly.

## Security & Configuration Tips
- **Environment**: Create a `.env` with `SECRET_KEY` for Flask; the app loads it via python‑dotenv.
- **MCP config**: `PROMPTBIN_PORT`, `PROMPTBIN_HOST`, `PROMPTBIN_LOG_LEVEL`, `PROMPTBIN_DATA_DIR`.
- **Dev Tunnels config**: `DEVTUNNEL_ENABLED`, `DEVTUNNEL_AUTO_START`, `DEVTUNNEL_RATE_LIMIT`, `DEVTUNNEL_RATE_WINDOW`, `DEVTUNNEL_LOG_LEVEL`.
- **Data safety**: Prompts are local files; review `.gitignore` to avoid committing sensitive data.
- **Rate limiting**: Built-in protection (5 attempts per IP per 30 minutes) with automatic tunnel shutdown.
- **Share tokens**: Cryptographically secure, ephemeral (reset on app restart).
- **Tunnel security**: Anonymous access only for explicitly shared prompts; private data remains local.
