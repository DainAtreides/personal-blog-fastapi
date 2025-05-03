from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import EmailStr


Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="posts")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(EmailStr, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    posts = relationship("Post", back_populates="user")
