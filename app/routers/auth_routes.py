from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserRead
from database import get_db
from auth import authenticate_user, get_current_user

auth_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@auth_router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.post("/login")
async def login(
        request: Request,
        identifier: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_db)):
    authenticated_user = await authenticate_user(identifier, password, db)
    request.session["user_id"] = authenticated_user.user_id
    return RedirectResponse(url="/", status_code=303)


@auth_router.get("/home")
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


@auth_router.get("/me", response_model=UserRead)
async def read_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    return UserRead.model_validate(user)


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
