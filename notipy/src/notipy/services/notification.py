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
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.deleted == False)
            .order_by(Notification.id.asc())
            .limit(100)
        )
    ).all()


class NewNotification(BaseModel):
    content: str


class UpdateNotification(BaseModel):
    viewed: Optional[bool]
    deleted: Optional[bool]


async def save_notification(
    notification: Notification, session: AsyncSession
) -> Notification:
    session.add(notification)
    await session.flush()
    await session.refresh(notification)
    return notification


async def create_notification(
    user_id: int, data: NewNotification, session: AsyncSession
) -> Notification:
    new_notification = Notification()
    new_notification.user_id = user_id
    new_notification.content = data.content
    return await save_notification(new_notification, session)


async def update_notification(
    id: int, user_id: int, data: UpdateNotification, session: AsyncSession
) -> Optional[Notification]:
    notification: Optional[Notification] = (
        await session.scalars(
            select(Notification)
            .where(Notification.id == id)
            .where(Notification.user_id == user_id)
            .limit(1)
        )
    ).first()
    if not notification:
        return None
    if data.viewed is not None:
        notification.viewed = data.viewed
    if data.deleted is not None:
        notification.deleted = data.deleted
    return await save_notification(notification, session)


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


class NotificationSchema(BaseModel):
    id: int
    content: str
    viewed: bool
    deleted: bool


async def notify_notification(
    user_id: int,
    notification: Notification,
    redis_client: redis.Redis,
):
    notification_data = NotificationSchema(
        id=notification.id,
        content=notification.content,
        deleted=notification.deleted,
        viewed=notification.viewed,
    )
    await notify_user(user_id, notification_data, redis_client)
