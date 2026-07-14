import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# To prevent circular imports
if TYPE_CHECKING:
    from .user import User
    from .task import Task


class Project(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="projects")

    tasks: Mapped[list["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
