from typing import AsyncIterator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from notipy.models import Notification
from pydantic import BaseModel
from notipy.utils.db import redis
from redis.asyncio.client import PubSub


async def get_user_notifications(
    user_id: int, session: AsyncSession
) -> list[Notification]:
    return (
        await session.scalars(
            select(Notification).where(Notification.user_id == user_id).limit(100)
        )
    ).all()


class NewNotification(BaseModel):
    content: str


async def create_notification(
    user_id: int, data: NewNotification, session: AsyncSession
) -> Notification:
    new_notification = Notification()
    new_notification.user_id = user_id
    new_notification.content = data.content
    session.add(new_notification)
    await session.flush()
    await session.refresh(new_notification)
    return new_notification


class NotificationMessage(BaseModel):
    channel: bytes
    data: bytes
    pattern: Optional[str]
    type: str


async def subscribe_to_user_messages(
    user_id: int,
    pub_sub: PubSub,
) -> AsyncIterator[NotificationMessage]:
    await pub_sub.subscribe(f"user-{user_id}")
    while True:
        msg = await pub_sub.get_message(ignore_subscribe_messages=True)
        if msg:
            notification_msg = NotificationMessage(**msg)
            yield notification_msg


async def notify_user(
    user_id: int,
    data: BaseModel,
    redis_client: redis.Redis,
):
    await redis_client.publish(f"user-{user_id}", data.model_dump_json())
