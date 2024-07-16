from datetime import datetime, timedelta, timezone, date
from typing import Annotated

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt
import os

from SQLManager import SQLManager
from CRUD import CRUD
# to get a string like this run:
# openssl rand -hex 32
load_dotenv()
SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "waflon": {
        "username": "waflon",
        "full_name": "Waflon Perez",
        "email": "waflon@fake.com",
        "hashed_password": "$2b$12$/.hWsd9zG3zivc67khS1q.G3s5g0HGgIyXzWYKGMApNgJxi6duUSG", #Clave hasheada al final del codigo, luego se pone acá
        "disabled": False
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


#CODIGO
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db = SQLManager()
@asynccontextmanager
async def lifespan(app: FastAPI): #solo verificamos la tabla al inicial el server
    db.connect()
    db.create_table()
    yield  # Code that runs before server starts

app = FastAPI(lifespan=lifespan)

# Validar la API KEY
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(fake_users_db, username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_users_db, username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


#Para crearse una hash_password
#clave_falsa = get_password_hash("os.getenv("PASSWORD"))
#print(clave_falsa)

@app.post("/api/v1/guardar")
async def agregar_libro(isbn, nombre, fecha_publicacion, editorial):
    try:
        crud = CRUD()
        respuesta = crud.nueva_entrada(isbn, nombre, fecha_publicacion, editorial)
        if respuesta["status"] == 200:
            return {}
        return {}
    except Exception as e:
        return {"error":e}
