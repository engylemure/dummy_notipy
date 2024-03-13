from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from notipy.models import Base
from typing import Optional


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    content: Mapped[str]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    viewed: Mapped[bool] = mapped_column(default=False)
    deleted: Mapped[bool] = mapped_column(default=False)
    user: Mapped[Optional["User"]] = relationship(back_populates="notifications")
