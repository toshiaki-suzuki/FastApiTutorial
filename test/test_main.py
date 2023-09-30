import uuid
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
    # レスポンスのtasksの順序が一定でないため、ソートしてから比較する
    response_tasks = response.json()["tasks"].sort(key=lambda x: x["id"])
    expected_tasks = tasks.sort(key=lambda x: x["id"])
    assert response_tasks == expected_tasks


def test_read_task_200(test_db):
    response = client.get(f"/tasks/{tasks[0]['id']}")
    assert response.status_code == 200
    assert response.json() == {"task": tasks[0]}


def test_read_task_404(test_db):
    # 既知の無効なUUIDを生成
    non_existent_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
    response = client.get(f"/tasks/{non_existent_uuid}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
