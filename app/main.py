import uuid
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, Task, TaskCreate

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "OK"}


@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {
        "tasks": [{
            "id": str(task.id),
            "name": task.name,
            "status": task.status
        }
            for task in tasks]}


@app.get("/tasks/{task_id}")
def read_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return {
            "task": {
                "id": str(task.id),
                "name": task.name,
                "status": task.status
            }
        }
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(name=task.name, status=task.status)
    try:
        db.add(db_task)
        db.commit()
        task_id = str(db_task.id)  # Save the id before closing the session
        task_name = db_task.name
        task_status = db_task.status
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return {
        "task": {
            "id": task_id,
            "name": task_name,
            "status": task_status
        }
    }


@app.put("/tasks/{task_id}")
def update_task(
        task_id: uuid.UUID,
        task: TaskCreate,
        db: Session = Depends(get_db)):
    # データベースからタスクを取得します
    db_task = db.query(Task).filter(Task.id == task_id).first()
    # データが存在する場合は、更新して返します
    if db_task:
        # タスクの名前とステータスを更新します
        db_task.name = task.name
        db_task.status = task.status
        try:
            # データベースを更新します
            db.commit()
            # 更新されたタスクを返します
            task_id = str(db_task.id)
            task_name = db_task.name
            task_status = db_task.status
        except Exception as e:
            # データベースの更新に失敗した場合は、ロールバックします
            db.rollback()
            raise e
        finally:
            # セッションを閉じます
            db.close()
        return {
            "task": {
                "id": task_id,
                "name": task_name,
                "status": task_status
            }
        }
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    # データベースからタスクを取得します
    db_task = db.query(Task).filter(Task.id == task_id).first()
    # データが存在する場合は、削除して返します
    if db_task:
        try:
            # データベースからタスクを削除します
            db.delete(db_task)
            db.commit()
        except Exception as e:
            # データベースの更新に失敗した場合は、ロールバックします
            db.rollback()
            raise e
        finally:
            # セッションを閉じます
            db.close()
        # 削除されたタスクを返します
        message = f"Task {db_task.name} was deleted"
        return message
    raise HTTPException(status_code=404, detail="Task not found")
