import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

DATABASE_URL = f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    status = Column(String(50))


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

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


@app.get("/")
def root():
    return {"message": "OK"}


@app.get("/tasks")
def read_tasks():
    return {"tasks": tasks}


@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    for t in tasks:
        if t["id"] == task_id:
            return {"task": t}

    raise HTTPException(status_code=404, detail="Task not found")
