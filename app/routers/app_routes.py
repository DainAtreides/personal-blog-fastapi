from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserAuth
from database import get_db
from auth import authenticate_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/create")
async def create(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


@router.get("/read")
async def read(request: Request):
    return templates.TemplateResponse("read_post.html", {"request": request})


@router.get("/update")
async def update(request: Request):
    return templates.TemplateResponse("update_post.html", {"request": request})


@router.get("/delete")
async def delete(request: Request):
    return templates.TemplateResponse("delete_post.html", {"request": request})


@router.post("/login")
async def login(user: UserAuth, db: AsyncSession = Depends(get_db)):
    authenticated_user = await authenticate_user(user.email, user.password, db)
    return {
        "user_id": authenticated_user.user_id,
        "username": authenticated_user.username,
        "email": authenticated_user.email
    }
