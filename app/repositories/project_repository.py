import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectUpdate


class ProjectRepository:
    async def create(self, project: Project, session: AsyncSession) -> Project:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        return project

    async def get_all(self, session: AsyncSession):
        projects = await session.execute(select(Project).order_by(Project.title))

        return projects.scalars().all()

    async def get_by_id(self, project_id: uuid.UUID, session: AsyncSession) -> Project:
        project = await session.execute(select(Project).where(Project.id == project_id))
        return project.scalar_one_or_none()

    async def update(self, task_id: uuid.UUID, task: ProjectUpdate) -> Project:
        pass

    async def delete(self, project_id: uuid.UUID, session: AsyncSession):
        pass


project_repository = ProjectRepository()
