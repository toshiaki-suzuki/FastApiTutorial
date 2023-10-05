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
