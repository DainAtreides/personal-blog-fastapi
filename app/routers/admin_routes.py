from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from auth import get_current_user, check_admin
from crud.crud_user import read_non_admin_users, delete_user
from database import get_db


admin_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@admin_router.get("/admin/users")
async def list_users(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    await check_admin(user)
    users_data = await read_non_admin_users(db)
    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users_data})


@admin_router.post("/admin/users/{user_id}/delete")
async def delete_user_route(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    await check_admin(user)
    await delete_user(user_id, db)
    return RedirectResponse(url="/admin/users", status_code=303)
