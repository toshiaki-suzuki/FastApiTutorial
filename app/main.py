# 必要なモジュールをインポートします。
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer, String
from .database import Base, engine, SessionLocal

# Taskという名前のモデルを定義します。


class Task(Base):
    __tablename__ = "tasks"  # テーブル名はtasksです。

    # タスクの各属性を定義します。各タスクにはid, name, およびstatusがあります。
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    status = Column(String(50))


# FastAPIのインスタンスを作成します。
app = FastAPI()

# アプリケーションの起動時に、データベーステーブルを作成します。


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# サンプルのタスクを定義します。
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

# ルートURLにアクセスしたときに、"OK"メッセージを返します。


@app.get("/")
def root():
    return {"message": "OK"}

# /tasks URLにGETリクエストを送信すると、すべてのタスクを返します。


@app.get("/tasks")
def read_tasks():
    return {"tasks": tasks}

# /tasks/{task_id} URLにGETリクエストを送信すると、指定されたIDのタスクを返します。
# タスクが見つからない場合は、404エラーを返します。


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return {"task": t}
    raise HTTPException(status_code=404, detail="Task not found")
