from fastapi import Depends, HTTPException
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


async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostRead.model_validate(post)
