import uuid

tasks = [
    {
        "id": str(uuid.uuid4()),  # UUIDを文字列に変換
        "name": "test1",
        "status": 1
    },
    {
        "id": str(uuid.uuid4()),  # UUIDを文字列に変換
        "name": "test2",
        "status": 0
    },
]
