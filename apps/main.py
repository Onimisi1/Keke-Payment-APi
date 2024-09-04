from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime

import models
from database import engine, get_db
from models import User
from schemas import UserPublic, UserCreate, Token
from utils import hash_password, authenticate_user, create_access_token


app = FastAPI()


models.Base.metadata.create_all(bind=engine)


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/token')


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def home(db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).all()
    return user


@app.post("/create_user")
async def create_user(db: db_dependency, user_data: UserCreate):

    if db.query(User).filter(User.email==user_data.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')
    elif db.query(User).filter(User.username==user_data.username).first():
        raise HTTPException(status_code=400, detail='Username already exists')
    elif db.query(User).filter(User.phone_number==user_data.phone_number).first():
        raise HTTPException(status_code=400, detail='Phone number already exists')
    elif db.query(User).filter(User.unique_no==user_data.unique_no).first():
        raise HTTPException(status_code=400, detail='Your identification number must be unique')
    

    if user_data.role not in ["student", "driver"]:
        raise HTTPException(status_code=400, detail='Role must be a student or driver')

    new_user = User(
        username = user_data.username,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        phone_number = user_data.phone_number,
        email = user_data.email,
        role = user_data.role,
        unique_no = user_data.unique_no,
        hashed_password = hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/token", response_model=Token)
async def login_access_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid credentials')
    data = {
        'sub': user.username,
        'id': user.id,
        'role': user.role
    }
    access_token = create_access_token(data)

    return access_token