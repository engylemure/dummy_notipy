from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from notipy.models.user import User


async def get_user_by_id(id: int, session: AsyncSession) -> Optional[User]:
    return await session.scalar(select(User).where(User.id == id).limit(1))
