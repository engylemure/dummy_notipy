from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect
from notipy.models import User
from pydantic import BaseModel
from notipy.utils.db import DBSessionDep, RedisDep
from notipy.services import user as user_service, notification as notification_service
import asyncio

router = APIRouter(
    prefix="/users",
    tags=["users"],
    redirect_slashes=False,
)


async def _check_user_exists(id: int, session: DBSessionDep) -> User:
    user = await user_service.get_user_by_id(id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {id} not found",
        )
    return user


@router.get("/{id}/notifications")
async def user_notifications(id: int, db: DBSessionDep):
    await _check_user_exists(id, db)
    return await notification_service.get_user_notifications(id, db)


class NotificationSchema(BaseModel):
    id: int
    content: str
    viewed: bool
    deleted: bool


@router.post("/{id}/notifications")
async def create_user_notification(
    id: int,
    data: notification_service.NewNotification,
    db: DBSessionDep,
    redis: RedisDep,
):
    await _check_user_exists(id, db)
    new_notification = await notification_service.create_notification(id, data, db)
    await db.commit()
    await db.refresh(new_notification)
    print(new_notification)
    await notification_service.notify_notification(id, new_notification, redis)
    return new_notification


@router.patch("/{user_id}/notifications/{notification_id}")
async def update_user_notification(
    user_id: int,
    notification_id: int,
    data: notification_service.UpdateNotification,
    db: DBSessionDep,
    redis: RedisDep,
):
    await _check_user_exists(user_id, db)
    updated_notification = await notification_service.update_notification(
        notification_id, user_id, data, db
    )
    await db.commit()
    if updated_notification:
        await db.refresh(updated_notification)
        await notification_service.notify_notification(
            user_id, updated_notification, redis
        )
    return updated_notification


@router.websocket("/{id}/notifications-ws")
async def websocket_endpoint(
    id: int, websocket: WebSocket, db: DBSessionDep, redis: RedisDep
):
    await _check_user_exists(id, db)
    await websocket.accept()

    async def _handler():
        pub_sub = redis.pubsub()
        try:
            async for msg in notification_service.subscribe_to_user_messages(
                id, pub_sub
            ):
                if msg.type == "message":
                    await websocket.send_text(msg.data.decode())
        except Exception:
            await pub_sub.close()

    asyncio.create_task(_handler())

    while True:
        try:
            await websocket.receive()
        except Exception:
            break
