from fastapi import FastAPI, HTTPException

app = FastAPI()

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
