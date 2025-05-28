from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from database import get_db
from crud.crud_comment import create_comment, update_comment, delete_comment, get_user_by_comment
from schemas import CommentCreate, CommentUpdate

comment_router = APIRouter(prefix="/posts")


@comment_router.post("/{post_id}/comments")
async def add_comment(
        post_id: int,
        content: str = Form(...),
        request: Request = None,
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    comment_create = CommentCreate(content=content)
    await create_comment(post_id, user_id, comment_create, db)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@comment_router.post("/{post_id}/comments/{comment_id}/edit")
async def edit_comment(
        post_id: int,
        comment_id: int,
        content: str = Form(...),
        request: Request = None,
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    comment_update = CommentUpdate(content=content)
    updated_comment = await update_comment(comment_id, comment_update, db)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@comment_router.post("/{post_id}/comments/{comment_id}/delete")
async def remove_comment(
        post_id: int,
        comment_id: int,
        request: Request = None,
        db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    owner_id = await get_user_by_comment(comment_id, db)
    if owner_id is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if owner_id != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this comment")
    await delete_comment(comment_id, db)
    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)
