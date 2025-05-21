from fastapi import HTTPException
from models import Post
from schemas import PostCreate, PostRead, PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional


async def get_post_by_id(post_id: int, db: AsyncSession) -> Post:
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(
            Post.post_id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def create_post(post: PostCreate, user_id: int, db: AsyncSession) -> PostRead:
    new_post = Post(title=post.title, content=post.content, user_id=user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    result = await db.execute(
        select(Post).options(selectinload(Post.user)).where(
            Post.post_id == new_post.post_id
        )
    )
    post_with_user = result.scalar_one()
    return PostRead.model_validate(post_with_user)


async def read_post(post_id: int, db: AsyncSession) -> PostRead:
    post = await get_post_by_id(post_id, db)
    return PostRead.model_validate(post)


async def read_posts(
    db: AsyncSession,
    limit: int,
    offset: int,
    user_id: Optional[int] = None
) -> List[PostRead]:
    query = select(Post).options(selectinload(Post.user)).order_by(
        Post.created_at.desc()).offset(offset).limit(limit)

    if user_id is not None:
        query = query.where(Post.user_id == user_id)

    result = await db.execute(query)
    posts = result.scalars().all()
    return [PostRead.model_validate(post) for post in posts]


async def update_post(post_id: int, new_post: PostUpdate, db: AsyncSession) -> PostRead:
    post = await get_post_by_id(post_id, db)
    if new_post.title is not None:
        post.title = new_post.title
    if new_post.content is not None:
        post.content = new_post.content
    await db.commit()
    await db.refresh(post)
    return PostRead.model_validate(post)


async def delete_post(post_id: int, db: AsyncSession) -> PostRead:
    post = await get_post_by_id(post_id, db)
    deleted_post = PostRead.model_validate(post)
    await db.delete(post)
    await db.commit()
    return deleted_post
