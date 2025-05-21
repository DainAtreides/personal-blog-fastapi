from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from database import get_db
from crud.crud_post import read_posts
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request, db: AsyncSession = Depends(get_db)):
    posts = await read_posts(limit=100, offset=0, db=db)
    return templates.TemplateResponse("home.html", {"request": request, "posts": posts})
