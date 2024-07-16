from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    name:str

@app.get("/crear/")
async def crear(data: Data):
    return {data}


@app.get("/test/{item_id}")
async def test(item_id: str):
    return {"hola": item_id}