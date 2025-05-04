from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from schemas import UserCreate, UserRead
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    def hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email,
                    hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserRead.model_validate(new_user)
