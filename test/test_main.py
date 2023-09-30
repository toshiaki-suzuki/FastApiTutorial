import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, Task
from app.database import SessionLocal, DATABASE_URL

from .test_data import tasks

client = TestClient(app)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# pytestのフィクスチャを使用して、テスト前にデータベースを初期化しテストデータを追加します
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    for task in tasks:
        db.add(Task(id=task["id"], name=task["name"], status=task["status"]))
    db.commit()
    db.close()
    yield  # ここでテストが実行されます
    Base.metadata.drop_all(bind=engine)


def test_read_tasks_200(test_db):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == {"tasks": tasks}


def test_read_task_200(test_db):
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"task": tasks[0]}


def test_read_task_404(test_db):
    response = client.get("/tasks/0")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
