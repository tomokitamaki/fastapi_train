from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from passlib.context import CryptContext

from pydantic import BaseModel

import sqlite3
import pandas as pd

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "807c5ce4f68c0688c58695d457e0af57346787622ad8a7387d1926b749ff952b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# test_jwt.dbは以下のSQLで作成したtocksというテーブルと1つのレコードがある。ちなみにhashed_passwordは
# secretを get_password_hash 関数でハッシュ化したもの。
# 'CREATE TABLE stocks (username text, full_name text, email text, hashed_password text, disabled text)'
# 'insert into stocks values("johndoe", "John Doe", "johndoe@example.com", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", "False")
# conn = sqlite3.connect("test_jwt.db")
# cur = conn.cursor()
# name = ("johndoe",)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):

    return pwd_context.hash(password)


def get_user(username: str):
    # if username in db:
    #     user_dict = db[username]
    #     return UserInDB(**user_dict)
    conn = sqlite3.connect("test_jwt.db")
    # cur = conn.cursor()
    name = (username,)
    df = pd.read_sql_query(
            "select * from stocks where username = ?", conn, params=name
        )
    if df.empty:
        return False

    dict_data = pd.Series(df.iloc[0, :]).to_dict()

    return UserInDB(**dict_data)


# def authenticate_user(fake_db, username: str, password: str):
def authenticate_user(username: str, password: str):

    # user = get_user(fake_db, username)
    user = get_user(username)

    if not user:

        return False

    if not verify_password(password, user.hashed_password):

        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # user = authenticate_user(dict_data, form_data.username, form_data.password)
    user = authenticate_user(form_data.username, form_data.password)

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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/test")
# 認証をかけるにはDependsを使う
# async def test_get(user: User = Depends(get_current_user)):
# 認証をかけないならDependsを外す
async def test_get():

    return "test_return"
