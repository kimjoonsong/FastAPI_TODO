import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    save_todos([])
    yield
    save_todos([])

# ---------- GET ----------

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    todo = TodoItem(id=1, text="Test", completed=False)
    save_todos([todo.model_dump()])
    response = client.get("/todos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["text"] == "Test"

# ---------- POST ----------

def test_create_todo():
    response = client.post("/todos", json={"text": "New Task"})
    assert response.status_code == 201
    assert response.json()["text"] == "New Task"
    assert response.json()["completed"] is False

def test_create_todo_invalid():
    response = client.post("/todos", json={})
    assert response.status_code == 422

def test_create_todo_empty_text():
    response = client.post("/todos", json={"text": "   "})
    assert response.status_code == 400

# ---------- PUT ----------

def test_update_todo():
    save_todos([{"id": 1, "text": "Old", "completed": False}])
    updated = {"id": 1, "text": "Updated", "completed": True}
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated"
    assert response.json()["completed"] is True

def test_update_todo_not_found():
    response = client.put("/todos/999", json={"id": 999, "text": "X", "completed": False})
    assert response.status_code == 404

# ---------- DELETE ----------

def test_delete_todo():
    save_todos([{"id": 1, "text": "Delete me", "completed": False}])
    response = client.delete("/todos/1")
    assert response.status_code == 204

def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
