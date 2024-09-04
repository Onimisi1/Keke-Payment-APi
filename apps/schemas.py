from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(min_length=4)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)
    phone_number: str = Field(max_length=11)
    role: str
    unique_no: str = Field(max_length=10)
    

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserPublic(BaseModel):
    username: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


    