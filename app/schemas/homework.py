import uuid

from pydantic import BaseModel


class HomeworkCreate(BaseModel):
    title: str
    course_id: uuid.UUID


class HomeworkRead(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    course_id: uuid.UUID

    model_config = {
        "from_attributes": True
    }
