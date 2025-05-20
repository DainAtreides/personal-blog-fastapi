from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.responses import RedirectResponse
from schemas import PostCreate, PostRead, PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.crud_post import create_post, update_post, get_post_by_id
from auth import get_current_user
from models import User

post_router = APIRouter(prefix="/posts", tags=["Posts"])

templates = Jinja2Templates(directory="templates")


@post_router.get("/add-post")
async def add_post_form(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("posts/add_post.html", {"request": request})


@post_router.post("/", status_code=201)
async def add_post(
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    post = PostCreate(title=title, content=content)
    await create_post(post, user_id, db)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@post_router.get("/{post_id}")
async def view_post(
        post_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db)):
    post = await get_post_by_id(post_id, db)
    user_id = request.session.get("user_id")
    return templates.TemplateResponse(
        "posts/post_detail.html",
        {"request": request, "post": post, "user_id": user_id})


@post_router.get("/{post_id}/edit-post")
async def edit_post_form(
        post_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db)):
    user: User = await get_current_user(request, db)
    post = await get_post_by_id(post_id, db)
    if post.user_id != user.user_id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to edit this post")
    return templates.TemplateResponse("posts/edit_post.html", {"request": request, "post": post})


@post_router.post("/{post_id}/edit-post")
async def edit_post_submit(
        post_id: int,
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        db: AsyncSession = Depends(get_db)):
    user: User = await get_current_user(request, db)
    post = await get_post_by_id(post_id, db)
    if post.user_id != user.user_id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to edit this post")
    post_update = PostUpdate(title=title, content=content)
    await update_post(post_id, post_update, db)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=HTTP_303_SEE_OTHER)
