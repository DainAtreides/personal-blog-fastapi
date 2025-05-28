from fastapi import APIRouter, Depends, Query, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import User
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from crud.crud_user import create_user, read_user, read_users, update_user, delete_user, hash_password, verify_password
from crud.crud_post import read_posts
from typing import List, Optional
from models import GenderEnum
import shutil
import uuid
import os


user_router = APIRouter(prefix="/users", tags=["Users"])
templates = Jinja2Templates(directory="templates")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_gender(gender: str) -> GenderEnum:
    try:
        return GenderEnum(gender)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid gender selected")


def handle_avatar_upload(avatar: Optional[UploadFile]) -> str:
    if avatar is None or avatar.filename == "":
        return None
    if avatar.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, detail="Only image files are allowed")
    ext = os.path.splitext(avatar.filename)[-1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = f"static/avatars/{filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)
    return f"/static/avatars/{filename}"


async def process_user_form(
        username: str,
        gender: str,
        avatar_file: Optional[UploadFile],
        email: str,
        password: Optional[str] = None) -> dict:
    gender_enum = validate_gender(gender)
    avatar_url = handle_avatar_upload(avatar_file)
    user_data = {
        "username": username,
        "gender": gender_enum,
        "email": email
    }
    if password is not None:
        user_data["password"] = password
    if avatar_url is not None:
        user_data["avatar_url"] = avatar_url
    return user_data


@user_router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@user_router.post("/register")
async def register_user(
        request: Request,
        username: str = Form(...),
        gender: str = Form(...),
        avatar_url: Optional[UploadFile] = File(None),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: AsyncSession = Depends(get_db),):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"})
    user_data = await process_user_form(username, gender, avatar_url, email, password)
    user_create = UserCreate(**user_data)
    await create_user(user_create, db)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    request.session["user_id"] = user.user_id
    return RedirectResponse(url="/", status_code=303)


@user_router.get("/", response_model=List[UserRead])
async def get_users(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)):
    return await read_users(limit, offset, db)


@user_router.get("/{user_id}/show-profile", response_class=HTMLResponse)
async def show_profile(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await read_user(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    posts = await read_posts(user_id=user.user_id, limit=100, offset=0, db=db)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "posts": posts})


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
        request: Request,
        avatar_url: Optional[UploadFile],
        username: Optional[str] = Form(...),
        gender: str = Form(...),
        email: Optional[str] = Form(...),
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_data = await process_user_form(username, gender, avatar_url, email)
    user_update = UserUpdate(**user_data)
    await update_user(user_id, user_update, db)
    return RedirectResponse(url=f"/users/{user_id}/show-profile", status_code=303)


@user_router.get("/me/delete-confirm")
async def render_profile_delete(request: Request):
    return templates.TemplateResponse("profile_delete.html", {"request": request})


@user_router.post("/me/edit-profile/delete", status_code=200)
async def confirm_profile_delete(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    await delete_user(user_id, db)
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@user_router.get("/me/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return templates.TemplateResponse("change_password.html", {"request": request})


@user_router.post("/me/change-password")
async def change_password(
        request: Request,
        current_password: str = Form(...),
        new_password: str = Form(...),
        confirm_password: str = Form(...),
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(current_password, user.hashed_password):
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "error": "Current password is incorrect"
        })

    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "error": "New passwords do not match"
        })

    user.hashed_password = hash_password(new_password)
    await db.commit()
    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "success": "Password updated successfully"})
