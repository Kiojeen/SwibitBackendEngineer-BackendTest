import uuid
from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str


class ProjectRead(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ProjectUpdate(BaseModel):
    title: str | None = None


class ProjectPaginated(BaseModel):
    items: list[ProjectRead]
    total: int
    offset: int
    limit: int
