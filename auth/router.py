from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


from database import get_async_session
from auth.dependencies import require_admin, get_current_user
from auth.models import User
from auth.schemas import UserRead

router = APIRouter(prefix="/users", tags=["Users"])



@router.get("/", response_model=List[UserRead], dependencies=[Depends(require_admin)])
async def read_users(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_async_session)
):
    query = select(User).offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()
    return users



@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user



@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(db_user)
    await session.commit()
