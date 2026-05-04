import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from starlette.requests import Request


BASE_DIR = Path(__file__).resolve().parent
TODO_FILE = BASE_DIR / "todo.json"

app = FastAPI(title="Todo List App")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class TodoCreate(BaseModel):
    text: str


class TodoItem(BaseModel):
    id: int
    text: str
    completed: bool = False


def load_todos() -> list[dict]:
    if not TODO_FILE.exists():
        TODO_FILE.write_text("[]", encoding="utf-8")
        return []

    with TODO_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_todos(todos: list[dict]) -> None:
    with TODO_FILE.open("w", encoding="utf-8") as file:
        json.dump(todos, file, ensure_ascii=False, indent=2)


@app.get("/", response_class=HTMLResponse)
def read_index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/todos", response_model=list[TodoItem])
def get_todos() -> list[dict]:
    return load_todos()


@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoCreate) -> dict:
    text = todo.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Todo text cannot be empty.")

    todos = load_todos()
    next_id = max((item["id"] for item in todos), default=0) + 1
    new_todo = {"id": next_id, "text": text, "completed": False}
    todos.append(new_todo)
    save_todos(todos)
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoItem) -> dict:
    todos = load_todos()

    for index, current in enumerate(todos):
        if current["id"] == todo_id:
            updated_todo = {
                "id": todo_id,
                "text": todo.text.strip() or current["text"],
                "completed": todo.completed,
            }
            todos[index] = updated_todo
            save_todos(todos)
            return updated_todo

    raise HTTPException(status_code=404, detail="Todo item not found.")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    todos = load_todos()
    filtered_todos = [todo for todo in todos if todo["id"] != todo_id]

    if len(filtered_todos) == len(todos):
        raise HTTPException(status_code=404, detail="Todo item not found.")

    save_todos(filtered_todos)
