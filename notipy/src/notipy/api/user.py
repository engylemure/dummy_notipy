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
    notification_data = NotificationSchema(
        id=new_notification.id,
        content=new_notification.content,
        deleted=new_notification.deleted,
        viewed=new_notification.viewed,
    )
    await notification_service.notify_user(id, notification_data, redis)
    return new_notification


@router.websocket("/{id}/notifications/ws")
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
