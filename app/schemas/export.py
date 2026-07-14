import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.export import ExportStatus


class ExportRead(BaseModel):
    id: uuid.UUID
    status: ExportStatus
    file_path: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
