import json
from pathlib import Path

from prompt_manager import PromptManager


def make_pm(tmp_path, monkeypatch) -> PromptManager:
    # Use the tmp_path directly as data directory for testing
    return PromptManager(data_dir=str(tmp_path / "test-prompts"))


def test_save_and_get_prompt(tmp_path, monkeypatch):
    pm = make_pm(tmp_path, monkeypatch)

    data = {
        "title": "Test Prompt",
        "content": "Example content with tag and {{variable}}",
        "category": "coding",
        "description": "A simple test prompt",
        "tags": "alpha, beta",
    }

    prompt_id = pm.save_prompt(data)
    saved = pm.get_prompt(prompt_id)

    assert saved is not None
    assert saved["id"] == prompt_id
    assert saved["title"] == "Test Prompt"
    assert saved["category"] == "coding"
    assert saved["tags"] == ["alpha", "beta"]
    assert saved["created_at"] and saved["updated_at"]

    # File exists in expected category path
    expected_path = tmp_path / "test-prompts" / "coding" / f"{prompt_id}.json"
    assert expected_path.exists()
    assert json.loads(expected_path.read_text("utf-8"))["id"] == prompt_id


def test_list_and_delete_prompt(tmp_path, monkeypatch):
    pm = make_pm(tmp_path, monkeypatch)

    id1 = pm.save_prompt({
        "title": "One",
        "content": "foo",
        "category": "coding",
        "tags": "t1",
    })
    id2 = pm.save_prompt({
        "title": "Two",
        "content": "bar",
        "category": "writing",
        "tags": "t2",
    })

    all_prompts = pm.list_prompts()
    assert {p["id"] for p in all_prompts} >= {id1, id2}

    coding_only = pm.list_prompts("coding")
    assert all(p["category"] == "coding" for p in coding_only)

    assert pm.delete_prompt(id1) is True
    assert pm.get_prompt(id1) is None


def test_search_prompts(tmp_path, monkeypatch):
    pm = make_pm(tmp_path, monkeypatch)

    pm.save_prompt({
        "title": "Searchable",
        "content": "This content has a unique needle",
        "category": "analysis",
        "tags": "search,example",
    })
    pm.save_prompt({
        "title": "Other",
        "content": "Nothing to see here",
        "category": "coding",
        "tags": "misc",
    })

    results = pm.search_prompts("needle")
    assert len(results) == 1
    assert "needle" in results[0]["content"]

    # Empty query returns full listing
    all_results = pm.search_prompts("")
    assert len(all_results) == len(pm.list_prompts())

