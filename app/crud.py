from fastapi import Depends
from database import get_db
from models import Post
from schemas import PostCreate, PostRead
from sqlalchemy.ext.asyncio import AsyncSession


async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)) -> PostRead:
    new_post = Post(title=post.title, content=post.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return PostRead.model_validate(new_post)
