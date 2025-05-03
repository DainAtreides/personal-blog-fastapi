from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    created_at: datetime


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostRead(PostBase):
    post_id: int
    user_id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserRead(UserBase):
    user_id: int

    class Config:
        orm_mode = True
