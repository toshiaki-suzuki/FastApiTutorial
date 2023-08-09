from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
async def read_items(
    *,
    # パスパラメータのバリデーション
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str,
    size: Annotated[float, Query(gt=0, lt=10.5)],  # クエリパラメータのバリデーション
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

# http://127.0.0.1:8000/items/10?q=hoge&size=1
