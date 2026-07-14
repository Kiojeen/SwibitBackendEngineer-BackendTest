import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export
from app.models.user import User
from app.repositories.export_repository import export_repository


class ExportService:

    async def create_export(self, user: User, session: AsyncSession) -> Export:
        export = Export(user_id=user.id)
        return await export_repository.create(export=export, session=session)

    async def get_exports(self, user: User, session: AsyncSession, offset: int = 0, limit: int = 10):
        return await export_repository.get_by_user_id(user_id=user.id, session=session, offset=offset, limit=limit)

    async def get_export_by_id(self, export_id: uuid.UUID, user: User, session: AsyncSession) -> Export:
        export = await export_repository.get_by_id(export_id=export_id, session=session)
        if export is None:
            raise HTTPException(status_code=404, detail="Export not found.")
        if export.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this export.")
        return export


export_service = ExportService()
