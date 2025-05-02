from fastapi import APIRouter, Depends
from schemas import PostCreate, PostRead
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import create_post, read_post


post_router = APIRouter(prefix="/posts", tags=["Posts"])


@post_router.post("/", response_model=PostRead)
async def create_new_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    return await create_post(post, db)


@post_router.get("/{post_id}", response_model=PostRead)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    return await read_post(post_id, db)
