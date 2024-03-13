from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from typing import Any, Optional


Base = declarative_base()


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    content: Mapped[str]
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    viewed: Mapped[bool] = mapped_column(default=False)
    deleted: Mapped[bool] = mapped_column(default=False)
    # user: Mapped[Optional[Any]] = relationship(back_poupulates="notifications")


class User(Base):
    __tablename__ = "users"
    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    name: Mapped[str]
    # notifications: Mapped[Optional[list[Notification]]] = relationship(
    #     back_populates="user"
    # )
