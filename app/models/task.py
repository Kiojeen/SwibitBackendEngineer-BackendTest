import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Text

from app.db.base import Base

# To prevent circular imports
if TYPE_CHECKING:
    from .project import Project


class Task(Base):
    __tablename__ = "task"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="pending")

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"))

    project: Mapped["Project"] = relationship(back_populates="tasks")
