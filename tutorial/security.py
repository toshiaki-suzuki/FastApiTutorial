from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
# OAuth2.0による基本的な認証が簡単に実装できる
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
