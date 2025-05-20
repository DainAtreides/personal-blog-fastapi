from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from routers.app_routes import router
from routers.post_routes import post_router
from routers.user_routes import user_router
from routers.auth_routes import auth_router
from routers.admin_routes import admin_router
from init_db import init_model
from config import SECRET_KEY
from starlette.middleware.sessions import SessionMiddleware


async def lifespan(app: FastAPI):
    await init_model()
    yield

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(router)
app.include_router(post_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return templates.TemplateResponse(
            "error.html", {"request": request, "detail": exc.detail, "status_code": exc.status_code}, status_code=401)
    elif exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html", {"request": request, "detail": exc.detail, "status_code": exc.status_code}, status_code=403)
    elif exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html", {"request": request, "detail": exc.detail, "status_code": exc.status_code}, status_code=404)
    return await http_exception_handler(request, exc)
