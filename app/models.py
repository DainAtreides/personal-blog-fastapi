from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Enum, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum


Base = declarative_base()


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String, default="user")
    avatar_url = Column(String, nullable=True,
                        default="/static/avatars/default.png")
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)

    posts = relationship("Post", back_populates="user",
                         cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "user.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey(
        "post.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "user.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
