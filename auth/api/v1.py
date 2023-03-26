import json
import sqlite3
from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, status, APIRouter, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from starlette.authentication import AuthenticationError
from asyncpg.exceptions import UniqueViolationError
from ormar.exceptions import NoMatch
from typing import Optional

from app.core.schemas import LoginResponse
from app.core.config import settings
from app.database import User, Repro
from auth.schemas import User as PDUser

from auth.helpers import authentication_required


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(Model, email, password):
    try:
        user = await Model.objects.get(email=email)
    except NoMatch as exe:
        raise AuthenticationError("Username or password is incorrect!")
    if not user.active:
        raise AuthenticationError("User is inactive or disabled by Admin!")
    verified = pwd_context.verify(password, user.hashed_password)
    if not verified:
        raise AuthenticationError("Username or password is incorrect!")
    return user


def get_access_token(data):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if not isinstance(data, str):
        data = json.dumps(data)
    access_token = create_access_token(
        data={"sub": data}, expires_delta=access_token_expires
    )
    return access_token


@router.post("/token", response_model=LoginResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await authenticate_user(User, form_data.username, form_data.password)
    except AuthenticationError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"error": str(error)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = get_access_token({"user_id": user.id, "username": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "credits": user.credits
    }


@router.post("/user")
# async def create_user(username: str = Body(), password: str = Body(), ):
async def create_user(user_data: PDUser = Body()):
    hashed_password = pwd_context.hash(user_data.password)
    print(hashed_password)
    try:
        user = await User.objects.create(hashed_password=hashed_password, **user_data.dict(exclude={'password'}))
    except (UniqueViolationError, sqlite3.IntegrityError) as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the given email already exists!"
        )
    access_token = get_access_token({"user_id": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user/{user_id}", dependencies=[Depends(authentication_required)])
async def get_user(user_id, request: Request):
    if request.user.id == user_id:
        return "Complete User Details"
    HTTPException(status.HTTP_404_NOT_FOUND, detail={"error": "User not found"})


@router.get("/logout", dependencies=[Depends(authentication_required)])
async def logout_user(request: Request):
    return "Logged Out"


@router.get("/callback")
async def callback():
    return "Callback"


@router.post("/reprography")
# async def create_user(username: str = Body(), password: str = Body(), ):
async def create_user(user_data: PDUser = Body()):
    hashed_password = pwd_context.hash(user_data.password)
    print(hashed_password)
    try:
        user = await Repro.objects.create(hashed_password=hashed_password, **user_data.dict(exclude={'password'}))
    except (UniqueViolationError, sqlite3.IntegrityError) as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the given email already exists!"
        )
    access_token = get_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/reprography/token", response_model=LoginResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await authenticate_user(Repro, form_data.username, form_data.password)
    except AuthenticationError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"error": str(error)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = get_access_token({"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "credits": user.credits
    }
