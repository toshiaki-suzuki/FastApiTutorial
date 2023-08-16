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


def test_read_tasks():

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}
