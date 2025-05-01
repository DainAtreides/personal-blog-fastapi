from fastapi import FastAPI
from routers.app_routes import router

app = FastAPI()

app.include_router(router)
