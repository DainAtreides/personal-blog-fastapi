from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserAuth, UserRead
from database import get_db
from auth import authenticate_user, get_current_user

auth_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@auth_router.post("/login")
async def login(user: UserAuth, request: Request, db: AsyncSession = Depends(get_db)):
    authenticated_user = await authenticate_user(user.email, user.password, db)
    request.session["user_id"] = authenticated_user.user_id
    return UserRead.model_validate(authenticated_user)


@auth_router.get("/me", response_model=UserRead)
async def read_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    return UserRead.model_validate(user)


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Successfully logged out"}
