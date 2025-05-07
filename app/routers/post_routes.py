from fastapi import APIRouter, Depends, Query, HTTPException
from schemas import PostCreate, PostRead, PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.crud_post import create_post, read_post, read_posts, update_post, delete_post
from auth import get_current_user
from models import User
from typing import List

post_router = APIRouter(prefix="/posts", tags=["Posts"])


@post_router.post("/", response_model=PostRead, status_code=201)
async def add_post(
        post: PostCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    return await create_post(post, db)


@post_router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await read_post(post_id, db)


@post_router.get("/", response_model=List[PostRead])
async def get_posts(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)):
    return await read_posts(limit, offset, db)


@post_router.patch("/{post_id}", response_model=PostRead)
async def patch_post(
        post_id: int,
        new_post: PostUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    post = await read_post(post_id, db)
    if post.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can't edit this post")
    return await update_post(post_id, new_post, db)


@post_router.delete("/{post_id}", response_model=PostRead, status_code=200)
async def remove_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    post = await read_post(post_id, db)
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, detail="You can't delete this post")
    return await delete_post(post_id, db)
