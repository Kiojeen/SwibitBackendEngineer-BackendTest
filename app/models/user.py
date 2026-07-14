from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="user", cascade="all, delete-orphan")