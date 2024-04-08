from datetime import timedelta, datetime
import datetime as dt
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from database import SessionLocal
from models import Users

router = APIRouter(
    prefix="/api/v1/auth",
    tags=['auth']
)

SECRET_KEY = "2a9191fc9ffeb3490013043e1643557edfefdb6b715af5dc47df30a4428c3c97"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str,
                        user_id: int,
                        role: str,
                        expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    encode = {
        "sub": username,
        "id": user_id,
        "role": role
    }
    expires = datetime.now(dt.UTC) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    phone_number: str


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {
            "username": username,
            "id": user_id,
            "user_role": user_role
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


# @router.get("/users", status_code=status.HTTP_200_OK)
# async def get_users(db: db_dependency):
#     users = db.query(Users).all()
#     return users


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: UserRequest):
    user_model = Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role='user',
        password=bcrypt_context.hash(user.password),
        is_active=True,
        phone_number=user.phone_number
    )

    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return False

    token = create_access_token(user.username, user.id, user.role)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return {"access_token": token, "token_type": "bearer"}
