# Repository Guidelines

## Project Structure & Module Organization
- app.py: Flask web app (routes, views).
- mcp_server.py: MCP server integrating PromptBin tools.
- prompt_manager.py / share_manager.py: File storage, sharing logic.
- templates/ and static/: UI templates and assets.
- prompts/: Local JSON prompt data, grouped by category (coding, writing, analysis).
- ai_docs/: Internal planning and prompts for future phases.

## Build, Test, and Development Commands
- Install deps: `uv sync` (requires Python 3.11+ and uv).
- Run web UI: `uv run python app.py` (http://localhost:5000).
- Run MCP server: `uv run python mcp_server.py` (MCP + web lifecycle).
- Lint/format: none enforced; see style section below.

## Coding Style & Naming Conventions
- Python style: PEP 8, 4‑space indents, descriptive names.
- Types: prefer type hints for public functions and return values.
- Modules: keep files focused (web in app.py, protocol in mcp_server.py, storage in prompt_manager.py).
- IDs: prompt files named `<id>.json` under `prompts/<category>/` (IDs generated like `YYYYMMDD_HHMMSS_xxxxxxxx`).
- Categories: use one of `coding`, `writing`, `analysis`.

## Testing Guidelines
- Current status: no formal test suite yet.
- If adding tests, use `pytest`; place tests in `tests/` and name files `test_*.py`.
- Prioritize unit tests for PromptManager (save/get/list/search/delete) and share token validation.
- Aim for clear, isolated tests over broad integration first.

## Commit & Pull Request Guidelines
- Commits: prefer Conventional Commits (e.g., `feat:`, `fix:`, `chore:`). Keep messages imperative and scoped.
- PRs: include a concise summary, linked issues, screenshots/gifs for UI changes, and repro/validation steps (commands and expected outcomes).
- Keep PRs small and cohesive; note any follow‑ups explicitly.

## Security & Configuration Tips
- Environment: create a `.env` with `SECRET_KEY` for Flask; the app loads it via python‑dotenv.
- MCP config via env: `PROMPTBIN_PORT`, `PROMPTBIN_HOST`, `PROMPTBIN_LOG_LEVEL`, `PROMPTBIN_DATA_DIR`.
- Data safety: prompts are local files; review `.gitignore` to avoid committing sensitive data.
