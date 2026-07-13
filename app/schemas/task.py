import uuid

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    project_id: uuid.UUID


class TaskRead(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    project_id: uuid.UUID

    model_config = {
        "from_attributes": True
    }
