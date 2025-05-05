from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserRead(UserBase):
    user_id: int

    model_config = {
        "from_attributes": True
    }


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


class RefreshTokenBase(BaseModel):
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class RefreshTokenCreate(RefreshTokenBase):
    token: str
    expires_at: datetime
    is_valid: bool = True


class RefreshTokenRead(RefreshTokenBase):
    token_id: int
    user: UserRead
    token: str
    expires_at: datetime
    is_valid: bool

    model_config = {
        "from_attributes": True
    }
