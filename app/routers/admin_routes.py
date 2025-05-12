from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth import get_current_user, check_admin
from models import User
from database import get_db
from schemas import UserRead

admin_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@admin_router.get("/admin/users")
async def list_users(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    await check_admin(user)
    result = await db.execute(select(User))
    users = result.scalars().all()
    users_data = [UserRead.model_validate(user) for user in users]
    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users_data})
