import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.export import Export


class ExportRepository:

    async def create(self, export: Export, session: AsyncSession) -> Export:
        session.add(export)
        await session.commit()
        await session.refresh(export)
        return export

    async def get_by_id(self, export_id: uuid.UUID, session: AsyncSession) -> Export | None:
        result = await session.execute(select(Export).where(Export.id == export_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID, session: AsyncSession, offset: int = 0, limit: int = 10):
        result = await session.execute(
            select(Export)
            .where(Export.user_id == user_id)
            .order_by(Export.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_status(self, export_id: uuid.UUID, status: str, session: AsyncSession,
                            file_path: str | None = None) -> Export | None:
        export = await self.get_by_id(export_id=export_id, session=session)
        if export is None:
            return None
        export.status = status
        if file_path is not None:
            export.file_path = file_path
        await session.commit()
        await session.refresh(export)
        return export


export_repository = ExportRepository()
