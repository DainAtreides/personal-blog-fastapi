from fastapi import Depends, HTTPException
from database import get_db
from models import Post
from schemas import PostCreate, PostRead, PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List


async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)) -> PostRead:
    new_post = Post(**post.model_dump())
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return PostRead.model_validate(new_post)


async def read_post(post_id: int, db: AsyncSession = Depends(get_db)) -> PostRead:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostRead.model_validate(post)


async def read_posts(limit: int, offset: int, db: AsyncSession = Depends(get_db)) -> List[PostRead]:
    result = await db.execute(select(Post).offset(offset).limit(limit))
    posts = result.scalars().all()
    if not posts:
        raise HTTPException(status_code=404, detail="Posts not found")
    return [PostRead.model_validate(post) for post in posts]


async def update_post(post_id: int, new_post: PostUpdate, db: AsyncSession = Depends(get_db)) -> PostRead:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if new_post.title is not None:
        post.title = new_post.title
    if new_post.content is not None:
        post.content = new_post.content
    await db.commit()
    await db.refresh(post)
    return PostRead.model_validate(post)


async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)) -> PostRead:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    deleted_post = PostRead.model_validate(post)
    await db.delete(post)
    await db.commit()
    return deleted_post
