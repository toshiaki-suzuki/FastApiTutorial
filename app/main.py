import uuid
from fastapi import FastAPI, HTTPException, Depends, Path
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import Task

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
    return {"tasks": [{"id": str(task.id), "name": task.name, "status": task.status} for task in tasks]}


@app.get("/tasks/{task_id}")
def read_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return {"task": {"id": str(task.id), "name": task.name, "status": task.status}}
    raise HTTPException(status_code=404, detail="Task not found")
