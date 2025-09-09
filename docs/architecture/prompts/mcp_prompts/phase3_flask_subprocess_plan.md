# Phase 3: Flask Subprocess Integration — Implementation Plan (Hardcoded‑First)

## Goal
- Launch, monitor, and gracefully manage the Flask app from the MCP server with reliable health checks, restart/backoff, port management, and clean shutdown—while preserving standalone `app.py` behavior.

## Configuration Philosophy
- Hardcoded‑first: Prefer code defaults and explicit CLI arguments.
- No environment variables for primary config; allow optional env fallback only for local/manual runs.
- Single source of truth lives in code (constants or a small `config.py`).

## Milestones
- M1: Health/status endpoints in Flask + env-driven config.
- M2: `FlaskManager` (spawn/monitor/restart/shutdown) with psutil.
- M3: Wire into `mcp_server.py` with structured logging.
- M4: Port conflict handling, recovery/backoff, and tests.

## Flask App Changes
- Endpoints:
  - `GET /health`: returns JSON `{ status, uptime, mode, version, prompts_count }`.
  - `GET /mcp-status`: returns MCP integration mode (`mcp-managed` or `standalone`).
- Config intake: use `argparse` CLI flags with code defaults; only read env as last‑resort fallback in standalone runs.
  - Flags: `--host`, `--port`, `--mode`, `--log-level`, `--data-dir` (all optional; defaults in code).
- Uptime: track app start timestamp; version from `pyproject.toml` with code fallback to `0.1.0`.
- Defaults: if `--mode mcp-managed`, force `debug=False` and bind to provided host/port.

## FlaskManager (new module `flask_manager.py`)
- start_flask():
  - Find available port (start at default 5000, then probe upwards).
  - Spawn subprocess with explicit CLI args (no env):
    - `app.py --mode mcp-managed --host <host> --port <port> --log-level <level> --data-dir <dir>`.
  - Wait until `/health` healthy with timeout/retries; record startup time.
- stop_flask():
  - Send SIGTERM; wait up to shutdown timeout; SIGKILL on timeout.
  - Verify process tree is clean (no zombies) via psutil.
- restart_flask(): stop then start with exponential backoff.
- is_healthy(): HTTP `/health` with timeouts + psutil status; combine results.
- monitor_loop(): periodic health checks; restart on persistent failure; track restart counts.
- Helpers: `find_available_port(start=5000)`, basic CPU/RSS metrics via psutil for logging.

## MCP Server Integration (`mcp_server.py`)
- Centralize runtime config as an in‑code dict (no env required); expose constants for: host, base_port, health_check_interval, shutdown_timeout, log_level, data_dir.
- Instantiate `FlaskManager` with that config.
- In `start()`: `await manager.start_flask()` then `asyncio.create_task(manager.monitor_loop())`.
- In `shutdown()`: `await manager.stop_flask()` before exiting.
- Optional MCP resource: `promptbin://flask-status` returning `{healthy, port, restarts, uptime}`.

## Process Coordination & Config
- Shared via explicit CLI args from MCP to Flask; defaults hardcoded in both processes.
- Avoid env for primary flow; keep env only as a compatibility fallback in standalone mode.
- No HTTP admin control endpoint by default; restarts managed by `FlaskManager`.
- Both processes use the same file store (PromptManager); consider simple file locks on writes if needed.

## Error Handling & Recovery
- Startup failure: try N alternative ports, log errors, bubble degraded status.
- Health failures: retry R times; then restart with exponential backoff and max attempts.
- Crash loops: cap restarts; surface degraded mode and stop thrashing.
- Ensure no orphaned processes; always verify child termination.

## Logging & Metrics
- Structured lifecycle logs (start/stop, port decisions, health results, restart counts, startup durations).
- Respect hardcoded default log level; allow override via CLI flag.

## Testing Plan
- Unit: `find_available_port`, CLI arg parsing (Flask), health parsing, backoff schedule (mock HTTP + psutil).
- Integration (optional/marked): spawn Flask via manager, verify `/health`, kill process and confirm auto-restart, ensure shutdown cleans process tree.
- Keep default test run fast; skip long-running integration by default with markers.

## Acceptance Criteria
- MCP launches Flask, selects a free port, `/health` becomes healthy within timeout.
- Automatic restart on failure with capped backoff; clear logs of state changes.
- Graceful shutdown leaves no orphaned processes.
- `/health` and `/mcp-status` return accurate data.
- App remains runnable standalone; MCP + Flask share config and data reliably.
- Primary configuration is hardcoded or passed via CLI; env usage is optional only.
