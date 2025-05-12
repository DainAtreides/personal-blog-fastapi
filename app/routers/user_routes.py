from fastapi import APIRouter, Depends, Query, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import User
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud.crud_user import create_user, read_user, read_users, update_user, delete_user
from typing import List

user_router = APIRouter(prefix="/users", tags=["Users"])

templates = Jinja2Templates(directory="templates")


@user_router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@user_router.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        })

    user_data = UserCreate(username=username, email=email, password=password)
    await create_user(user_data, db)
    return RedirectResponse(url="/", status_code=303)


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await read_user(user_id, db)


@user_router.get("/", response_model=List[UserRead])
async def get_users(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)):
    return await read_users(limit, offset, db)


@user_router.get("/me/edit-profile", response_class=HTMLResponse)
async def edit_profile(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": user})


@user_router.post("/me/edit-profile")
async def update_profile(
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(None),
        request: Request = None,
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_update = UserUpdate(username=username, email=email, password=password)
    await update_user(user_id, user_update, db)
    return RedirectResponse(url="/", status_code=303)


@user_router.get("/me/delete-confirm")
async def confirm_delete_page(request: Request):
    return templates.TemplateResponse("confirm_delete.html", {"request": request})


@user_router.post("/me/edit-profile/delete", response_model=UserRead, status_code=200)
async def delete_profile(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    await delete_user(user_id, db)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
