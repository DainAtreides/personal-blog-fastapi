from fastapi import HTTPException
from models import Comment
from schemas import CommentCreate, CommentRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select


async def create_comment(
        post_id: int,
        user_id: int,
        comment_create: CommentCreate,
        db: AsyncSession) -> Comment:
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=comment_create.content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments_by_post(post_id: int, db: AsyncSession) -> list[CommentRead]:
    query = (
        select(Comment)
        .options(selectinload(Comment.user))
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    result = await db.execute(query)
    comments = result.scalars().all()
    return [CommentRead.model_validate(comment) for comment in comments]


async def delete_comment(comment_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = result.scalars().first()
    await db.delete(comment)
    await db.commit()
