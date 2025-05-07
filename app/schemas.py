from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('username', always=True)
    def check_username_length(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError('Username must be at least 2 characters long')
        return v


class UserRead(UserBase):
    user_id: int

    model_config = {
        "from_attributes": True
    }


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


class PostRead(PostBase):
    post_id: int
    user: UserRead

    model_config = {
        "from_attributes": True
    }
