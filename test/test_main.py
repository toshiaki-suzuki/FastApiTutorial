from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
tasks = [
    {
        "id": 1,
        "name": "test1",
        "status": "done"
    },
    {
        "id": 2,
        "name": "test2",
        "status": "done"
    },
]


def test_read_tasks_200():

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}


def test_read_task_200():

    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"task": tasks[0]}


def test_read_task_404():

    response = client.get("/tasks/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
