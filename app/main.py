from fastapi import FastAPI
from routers.app_routes import router
from routers.post_routes import post_router

app = FastAPI()

app.include_router(router)
app.include_router(post_router)
