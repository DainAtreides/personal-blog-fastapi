from fastapi import FastAPI
from routers.app_routes import router
from routers.post_routes import post_router
from routers.user_routes import user_router
from init_db import init_model


async def lifespan(app: FastAPI):
    await init_model()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(post_router)
app.include_router(user_router)
