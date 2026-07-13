import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate


class ProjectRepository:
    async def create(self, project: ProjectCreate, session: AsyncSession) -> Project:
        project_db = Project(
            title=project.title,
        )

        session.add(project_db)
        await session.commit()
        await session.refresh(project_db)

        return project_db

    async def get_all(self, session: AsyncSession):
        projects = await session.execute(select(Project).order_by(Project.title))

        return projects.scalars().all()

    async def get_by_id(self, project_id: uuid.UUID, session: AsyncSession) -> Project:
        project = await session.execute(select(Project).where(Project.id == project_id))
        return project.scalar_one_or_none()


project_repository = ProjectRepository()
