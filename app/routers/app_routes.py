from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/create-user")
async def create(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


@router.get("/read-post")
async def read(request: Request):
    return templates.TemplateResponse("read_post.html", {"request": request})


@router.get("/update-post")
async def update(request: Request):
    return templates.TemplateResponse("update_post.html", {"request": request})


@router.get("/delete-post")
async def delete(request: Request):
    return templates.TemplateResponse("delete_post.html", {"request": request})
