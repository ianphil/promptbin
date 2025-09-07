# Tests

Minimal pytest-based tests for `PromptManager`.

## Setup
- Install pytest (as a dev dependency):
  - Using uv: `uv add --dev pytest`
  - Or with pip (venv recommended): `pip install pytest`

## Run
- From repo root:
  - With uv: `uv run -m pytest -q`
  - With pytest directly: `pytest -q`

## Notes
- Tests monkeypatch `PromptManager.PROMPTS_DIR` to a temp directory, so no repo files are modified.
- Focus areas: save/get, list/delete, and basic search behavior.
