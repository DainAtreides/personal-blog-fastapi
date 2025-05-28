from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import GenderEnum


class FromORMBase(BaseModel):
    model_config = {
        "from_attributes": True
    }


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "user"
    avatar_url: Optional[str] = None
    gender: GenderEnum


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[GenderEnum] = None


class UserRead(UserBase, FromORMBase):
    user_id: int


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostRead(PostBase, FromORMBase):
    post_id: int
    created_at: datetime
    user: UserRead


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentRead(CommentBase, FromORMBase):
    comment_id: int
    post_id: int
    user: UserRead
    created_at: datetime
