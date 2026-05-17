import json
import pytest
from unittest.mock import patch, MagicMock

import app as flask_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Isolated test client with a fresh temp tasks file per test."""
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(flask_app, "TASKS_FILE", str(tasks_file))
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        yield c


@pytest.fixture
def mock_calendar():
    """Mock Google Tasks service that returns a fake created task."""
    mock_task = {"id": "task123"}
    mock_service = MagicMock()
    mock_service.tasks().insert().execute.return_value = mock_task
    with patch("app.get_tasks_service", return_value=mock_service):
        yield mock_service


def _post(client, payload, content_type="application/json"):
    return client.post("/tasks", json=payload, content_type=content_type)


def _seed(client, *titles):
    """Add tasks with minimal data and return their response bodies."""
    results = []
    for title in titles:
        r = _post(client, {"title": title})
        results.append(r.get_json())
    return results


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------

class TestGetTasks:
    def test_empty_list(self, client):
        r = client.get("/tasks")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_returns_all_tasks(self, client):
        _seed(client, "Task A", "Task B")
        r = client.get("/tasks")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) == 2
        assert data[0]["title"] == "Task A"
        assert data[1]["title"] == "Task B"


# ---------------------------------------------------------------------------
# POST /tasks — happy path
# ---------------------------------------------------------------------------

class TestAddTaskHappyPath:
    def test_minimal_task(self, client):
        r = _post(client, {"title": "Buy milk"})
        assert r.status_code == 201
        body = r.get_json()
        assert body["title"] == "Buy milk"
        assert body["done"] is False
        assert body["due"] is None
        assert body["description"] is None

    def test_with_description(self, client):
        r = _post(client, {"title": "Buy milk", "description": "Full fat"})
        assert r.status_code == 201
        assert r.get_json()["description"] == "Full fat"

    def test_task_persisted(self, client):
        _post(client, {"title": "Persisted"})
        tasks = client.get("/tasks").get_json()
        assert any(t["title"] == "Persisted" for t in tasks)

    def test_with_due_date(self, client):
        r = _post(client, {"title": "Meeting", "due": "2026-12-25T10:00"})
        assert r.status_code == 201
        body = r.get_json()
        assert body["due"] == "2026-12-25T10:00"
        assert body["due_formatted"] is not None

    def test_with_calendar(self, client, mock_calendar):
        r = _post(client, {"title": "Meeting", "due": "2026-12-25T10:00"})
        assert r.status_code == 201
        assert r.get_json()["calendar_event_id"] == "task123"

    def test_description_sent_to_calendar(self, client, mock_calendar):
        _post(client, {"title": "Meeting", "description": "Bring slides", "due": "2026-12-25T10:00"})
        call_args = mock_calendar.tasks().insert.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body")
        assert body["notes"] == "Bring slides"

    def test_empty_description_sent_to_calendar(self, client, mock_calendar):
        _post(client, {"title": "Meeting", "due": "2026-12-25T10:00"})
        call_args = mock_calendar.tasks().insert.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body")
        assert body["notes"] == ""

    def test_due_date_sent_to_calendar(self, client, mock_calendar):
        _post(client, {"title": "Meeting", "due": "2026-12-25T10:00"})
        call_args = mock_calendar.tasks().insert.call_args
        body = call_args.kwargs.get("body") or call_args[1].get("body")
        assert body["due"].startswith("2026-12-25")

    def test_calendar_failure_still_creates_task(self, client):
        with patch("app.get_tasks_service", side_effect=Exception("OAuth failed")):
            r = _post(client, {"title": "Meeting", "due": "2026-12-25T10:00"})
        assert r.status_code == 201
        body = r.get_json()
        assert body["title"] == "Meeting"
        assert body["calendar_event_id"] is None

    def test_whitespace_is_stripped_from_title(self, client):
        r = _post(client, {"title": "  Trimmed  "})
        assert r.status_code == 201
        assert r.get_json()["title"] == "Trimmed"


# ---------------------------------------------------------------------------
# POST /tasks — validation (including bugs)
# ---------------------------------------------------------------------------

class TestAddTaskValidation:
    def test_missing_title_key(self, client):
        r = _post(client, {"description": "No title"})
        assert r.status_code == 400
        assert "Title is required" in r.get_json()["error"]

    def test_empty_title(self, client):
        r = _post(client, {"title": ""})
        assert r.status_code == 400

    def test_whitespace_only_title(self, client):
        r = _post(client, {"title": "   "})
        assert r.status_code == 400

    def test_null_title(self, client):
        # Bug: used to crash with AttributeError — now must return 400
        r = _post(client, {"title": None})
        assert r.status_code == 400

    def test_no_body(self, client):
        # Bug: used to crash with AttributeError — now must return 400
        r = client.post("/tasks", data="", content_type="application/json")
        assert r.status_code == 400

    def test_null_description_does_not_crash(self, client):
        # Bug: used to crash with AttributeError
        r = _post(client, {"title": "Task", "description": None})
        assert r.status_code == 201
        assert r.get_json()["description"] is None

    def test_null_due_does_not_crash(self, client):
        # Bug: used to crash with AttributeError
        r = _post(client, {"title": "Task", "due": None})
        assert r.status_code == 201
        assert r.get_json()["due"] is None

    def test_non_dict_body(self, client):
        r = client.post("/tasks", data=json.dumps([1, 2, 3]), content_type="application/json")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /tasks/<index>
# ---------------------------------------------------------------------------

class TestToggleTask:
    def test_toggle_done_false_to_true(self, client):
        _seed(client, "Task A")
        r = client.patch("/tasks/0")
        assert r.status_code == 200
        assert r.get_json()["done"] is True

    def test_toggle_done_twice_returns_to_false(self, client):
        _seed(client, "Task A")
        client.patch("/tasks/0")
        r = client.patch("/tasks/0")
        assert r.get_json()["done"] is False

    def test_toggle_updates_persisted_state(self, client):
        _seed(client, "Task A")
        client.patch("/tasks/0")
        tasks = client.get("/tasks").get_json()
        assert tasks[0]["done"] is True

    def test_toggle_negative_index(self, client):
        _seed(client, "Task A")
        r = client.patch("/tasks/-1")
        assert r.status_code == 404

    def test_toggle_out_of_bounds(self, client):
        _seed(client, "Task A")
        r = client.patch("/tasks/99")
        assert r.status_code == 404

    def test_toggle_empty_list(self, client):
        r = client.patch("/tasks/0")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /tasks/<index>
# ---------------------------------------------------------------------------

class TestDeleteTask:
    def test_delete_only_task(self, client):
        _seed(client, "Task A")
        r = client.delete("/tasks/0")
        assert r.status_code == 200
        assert client.get("/tasks").get_json() == []

    def test_delete_returns_success(self, client):
        _seed(client, "Task A")
        body = client.delete("/tasks/0").get_json()
        assert body.get("success") is True

    def test_delete_shifts_indices(self, client):
        _seed(client, "A", "B", "C")
        client.delete("/tasks/0")          # remove A
        tasks = client.get("/tasks").get_json()
        assert len(tasks) == 2
        assert tasks[0]["title"] == "B"
        assert tasks[1]["title"] == "C"

    def test_delete_then_toggle_uses_shifted_index(self, client):
        _seed(client, "A", "B", "C")
        client.delete("/tasks/0")          # remove A → [B, C]
        r = client.patch("/tasks/0")       # toggle B (now at index 0)
        assert r.status_code == 200
        assert r.get_json()["done"] is True

    def test_delete_negative_index(self, client):
        _seed(client, "Task A")
        r = client.delete("/tasks/-1")
        assert r.status_code == 404

    def test_delete_out_of_bounds(self, client):
        _seed(client, "Task A")
        r = client.delete("/tasks/99")
        assert r.status_code == 404

    def test_delete_empty_list(self, client):
        r = client.delete("/tasks/0")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# PUT /tasks/<index> — edit task
# ---------------------------------------------------------------------------

class TestUpdateTask:
    def test_update_title(self, client):
        _seed(client, "Original")
        r = client.put("/tasks/0", json={"title": "Updated"})
        assert r.status_code == 200
        assert r.get_json()["title"] == "Updated"

    def test_update_persisted(self, client):
        _seed(client, "Original")
        client.put("/tasks/0", json={"title": "Updated"})
        assert client.get("/tasks").get_json()[0]["title"] == "Updated"

    def test_update_description(self, client):
        _seed(client, "Task")
        r = client.put("/tasks/0", json={"title": "Task", "description": "New desc"})
        assert r.get_json()["description"] == "New desc"

    def test_update_clears_description(self, client):
        _seed(client, "Task")
        client.put("/tasks/0", json={"title": "Task", "description": "desc"})
        r = client.put("/tasks/0", json={"title": "Task", "description": ""})
        assert r.get_json()["description"] is None

    def test_update_due_date(self, client):
        _seed(client, "Task")
        r = client.put("/tasks/0", json={"title": "Task", "due": "2026-12-25T10:00"})
        body = r.get_json()
        assert body["due"] == "2026-12-25T10:00"
        assert body["due_formatted"] is not None

    def test_update_empty_title(self, client):
        _seed(client, "Task")
        r = client.put("/tasks/0", json={"title": ""})
        assert r.status_code == 400

    def test_update_null_title(self, client):
        _seed(client, "Task")
        r = client.put("/tasks/0", json={"title": None})
        assert r.status_code == 400

    def test_update_out_of_bounds(self, client):
        r = client.put("/tasks/99", json={"title": "X"})
        assert r.status_code == 404

    def test_update_no_body(self, client):
        _seed(client, "Task")
        r = client.put("/tasks/0", data="", content_type="application/json")
        assert r.status_code == 400
