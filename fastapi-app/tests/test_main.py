import json
import pytest
from fastapi.testclient import TestClient
from main import app, TODO_FILE


@pytest.fixture(autouse=True)
def reset_todo_file(tmp_path, monkeypatch):
    """각 테스트마다 임시 todo.json을 사용하여 격리."""
    temp_file = tmp_path / "todo.json"
    temp_file.write_text("[]", encoding="utf-8")
    import main
    monkeypatch.setattr(main, "TODO_FILE", temp_file)
    yield


client = TestClient(app)


def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo():
    response = client.post("/todos", json={"text": "Test item"})
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test item"
    assert data["completed"] is False
    assert data["id"] == 1


def test_create_todo_empty_text():
    response = client.post("/todos", json={"text": "   "})
    assert response.status_code == 400


def test_create_multiple_todos():
    client.post("/todos", json={"text": "First"})
    client.post("/todos", json={"text": "Second"})
    response = client.get("/todos")
    assert len(response.json()) == 2


def test_update_todo():
    client.post("/todos", json={"text": "Original"})
    response = client.put("/todos/1", json={"id": 1, "text": "Updated", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated"
    assert data["completed"] is True


def test_update_todo_not_found():
    response = client.put("/todos/999", json={"id": 999, "text": "Nope", "completed": False})
    assert response.status_code == 404


def test_delete_todo():
    client.post("/todos", json={"text": "To delete"})
    response = client.delete("/todos/1")
    assert response.status_code == 204
    response = client.get("/todos")
    assert response.json() == []


def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
