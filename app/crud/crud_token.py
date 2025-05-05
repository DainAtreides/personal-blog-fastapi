from sqlalchemy.ext.asyncio import AsyncSession
from models import RefreshToken
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime, timezone


async def create_refresh_token(user_id: int, token: str, expires_at: datetime, db: AsyncSession) -> RefreshToken:
    new_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)
    return new_token


async def get_refresh_token_by_id(token_id: int, db: AsyncSession) -> RefreshToken:
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token_id == token_id))
    token = result.scalars().first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token


async def update_refresh_token(token_id: int, new_expires_at: datetime, db: AsyncSession) -> RefreshToken:
    token = await get_refresh_token_by_id(token_id, db)
    token.expires_at = new_expires_at
    await db.commit()
    await db.refresh(token)
    return token


async def delete_refresh_token(token_id: int, db: AsyncSession) -> None:
    token = await get_refresh_token_by_id(token_id, db)
    await db.delete(token)
    await db.commit()


async def is_token_valid(token: str, db: AsyncSession) -> bool:
    result = await db.execute(select(RefreshToken).filter(RefreshToken.token == token))
    token_obj = result.scalars().first()
    if not token_obj or token_obj.expires_at < datetime.now(timezone.utc):
        return False
    return token_obj.is_valid
