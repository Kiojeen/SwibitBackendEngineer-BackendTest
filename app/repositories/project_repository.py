import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectUpdate


class ProjectRepository:
    async def create(self, project: Project, session: AsyncSession) -> Project:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        return project

    async def get_by_user_id(self, user_id: uuid.UUID, session: AsyncSession, offset: int = 0, limit: int = 10):
        projects = await session.execute(
            select(Project).where(Project.user_id == user_id).order_by(Project.title).offset(offset).limit(limit)
        )
        return projects.scalars().all()

    async def count_by_user_id(self, user_id: uuid.UUID, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count()).select_from(Project).where(Project.user_id == user_id)
        )
        return result.scalar_one()

    async def get_by_id(self, project_id: uuid.UUID, session: AsyncSession) -> Project:
        project = await session.execute(select(Project).where(Project.id == project_id))
        return project.scalar_one_or_none()

    async def update(self, project_id: uuid.UUID, project_data: ProjectUpdate, session: AsyncSession) -> Project | None:
        project = await self.get_by_id(project_id=project_id, session=session)
        if project is None:
            return None
        if project_data.title is not None:
            project.title = project_data.title
        await session.commit()
        await session.refresh(project)
        return project

    async def delete(self, project_id: uuid.UUID, session: AsyncSession) -> bool:
        project = await self.get_by_id(project_id=project_id, session=session)
        if project is None:
            return False
        await session.delete(project)
        await session.commit()
        return True


project_repository = ProjectRepository()
