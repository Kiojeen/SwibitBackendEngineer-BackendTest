import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.export import ExportRead
from app.services.export_service import export_service
from app.tasks.user_tasks import export_user_data

router = APIRouter(
    prefix="/export",
    tags=["Export"],
)


@router.post("/", response_model=ExportRead)
async def create_export(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    export = await export_service.create_export(user=user, session=session)
    export_user_data.delay(str(export.id))
    return export


@router.get("/", response_model=list[ExportRead])
async def get_exports(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
        offset: int = 0,
        limit: int = 10,
):
    return await export_service.get_exports(user=user, session=session, offset=offset, limit=limit)


@router.get("/{export_id}", response_model=ExportRead)
async def get_export_by_id(
        export_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await export_service.get_export_by_id(export_id=export_id, user=user, session=session)


@router.get("/{export_id}/download")
async def download_export(
        export_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    export = await export_service.get_export_by_id(export_id=export_id, user=user, session=session)
    if export.status != "completed" or not export.file_path or not os.path.exists(export.file_path):
        raise HTTPException(status_code=404, detail="Export file not available.")
    return FileResponse(export.file_path, filename=os.path.basename(export.file_path), media_type="text/csv")
