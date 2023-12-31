import re
import uuid
import pytest
from collections import defaultdict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, Task
from app.database import DATABASE_URL

from .test_data import tasks

client = TestClient(app)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# pytestのフィクスチャを使用して、テスト前にデータベースを初期化しテストデータを追加します


@pytest.fixture(scope="function")
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

    # レスポンスの内容を確認
    results = response.json()["tasks"]

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    def count_pairs(pairs):
        counts = defaultdict(int)
        for pair in pairs:
            counts[pair] += 1
        return counts

    test_pairs = {(data["name"], data["status"]) for data in tasks}
    result_pairs = {(result["name"], result["status"]) for result in results}

    test_counts = count_pairs(test_pairs)
    result_counts = count_pairs(result_pairs)

    for result in results:
        # UUIDの形式を確認
        assert uuid_pattern.match(result["id"]) is not None
        # nameとstatusのペアがテストデータ内に存在するかを確認
        assert (result["name"], result["status"]) in test_pairs

    # 各ペアの出現回数が一致していることを確認
    assert test_counts == result_counts


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


def test_read_task_422(test_db):
    response = client.get("/tasks/invalid_value")
    assert response.status_code == 422


def test_create_task_200(test_db):
    data = {
        "name": "Test Task",
        "status": 1
    }

    response = client.post("/tasks", json=data)
    assert response.status_code == 200
    result = response.json()["task"]
    assert result["name"] == "Test Task"
    assert result["status"] == 1

    # UUIDの確認
    assert isinstance(result["id"], str)

    # 正しいUUIDの形式かどうかチェック
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    assert uuid_pattern.match(result["id"]) is not None


def test_create_task_too_short_name_422(test_db):
    data = {
        "name": "short",
        "status": 1
    }

    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json()[
        "detail"][0]["msg"] == "String should have at least 6 characters"


def test_create_task_too_long_name_422(test_db):
    data = {
        "name": "toooooooooooooooooooooooo_long_name_over_50characters",
        "status": 1
    }

    response = client.post("/tasks", json=data)
    assert response.status_code == 422
    assert response.json()[
        "detail"][0]["msg"] == "String should have at most 50 characters"


def test_update_task_200(test_db):
    data = {
        "name": "Updated Task",
        "status": 1
    }

    response = client.put(f"/tasks/{tasks[0]['id']}", json=data)
    assert response.status_code == 200
    result = response.json()["task"]
    assert result["name"] == "Updated Task"
    assert result["status"] == 1


def test_update_task_404(test_db):
    # 既知の無効なUUIDを生成
    non_existent_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
    data = {
        "name": "Updated Task",
        "status": 1
    }

    response = client.put(f"/tasks/{non_existent_uuid}", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task_invalid_path_parameter_422(test_db):
    data = {
        "name": "Updated Task",
        "status": 1
    }

    response = client.put("/tasks/invalid_value", json=data)
    assert response.status_code == 422


def test_update_task_too_short_name_422(test_db):
    data = {
        "name": "short",
        "status": 1
    }

    response = client.put(f"/tasks/{tasks[0]['id']}", json=data)
    assert response.json()[
        "detail"][0]["msg"] == "String should have at least 6 characters"


def test_update_task_too_long_name_422(test_db):
    data = {
        "name": "toooooooooooooooooooooooo_long_name_over_50characters",
        "status": 1
    }

    response = client.put(f"/tasks/{tasks[0]['id']}", json=data)
    assert response.json()[
        "detail"][0]["msg"] == "String should have at most 50 characters"


def test_update_task_invalid_status_422(test_db):
    data = {
        "name": "Updated Task",
        "status": 2
    }

    response = client.put("/tasks/invalid_value", json=data)
    assert response.status_code == 422


def test_delete_task_200(test_db):
    response = client.delete(f"/tasks/{tasks[0]['id']}")
    assert response.status_code == 200
    assert response.json() == f"Task {tasks[0]['name']} was deleted"
    # データベースからタスクが削除されていることを確認
    db = SessionLocal()
    db_task = db.query(Task).filter(Task.id == tasks[0]["id"]).first()
    db.close()
    assert db_task is None


def test_delete_task_404(test_db):
    # 既知の無効なUUIDを生成
    non_existent_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')

    response = client.delete(f"/tasks/{non_existent_uuid}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_task_invalid_path_parameter_422(test_db):
    response = client.delete("/tasks/invalid_value")
    assert response.status_code == 422
