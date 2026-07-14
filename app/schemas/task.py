import uuid

from pydantic import BaseModel

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    project_id: uuid.UUID
    status: TaskStatus = TaskStatus.pending


class TaskRead(BaseModel):
    id: uuid.UUID
    title: str
    status: TaskStatus
    project_id: uuid.UUID

    model_config = {
        "from_attributes": True
    }

class TaskUpdate(BaseModel):
    title: str | None = None
    status: TaskStatus | None = None
