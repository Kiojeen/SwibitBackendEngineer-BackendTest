import uuid

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str


class ProjectRead(BaseModel):
    id: uuid.UUID
    title: str

    model_config = {
        "from_attributes": True
    }

class ProjectUpdate(BaseModel):
    title: str | None = None
