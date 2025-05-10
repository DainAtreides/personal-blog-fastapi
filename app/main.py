from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.app_routes import router
from routers.post_routes import post_router
from routers.user_routes import user_router
from routers.auth_routes import auth_router
from init_db import init_model
from config import SECRET_KEY
from starlette.middleware.sessions import SessionMiddleware


async def lifespan(app: FastAPI):
    await init_model()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(router)
app.include_router(post_router)
app.include_router(user_router)
app.include_router(auth_router)
