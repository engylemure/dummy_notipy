from typing import Optional
from notipy.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"
    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    name: Mapped[str]
    notifications: Mapped[Optional[list["Notification"]]] = relationship(
        back_populates="user"
    )
