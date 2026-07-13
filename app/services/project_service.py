import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate, ProjectRead


class ProjectService:
    async def create_project(self, project: ProjectCreate, session: AsyncSession) -> ProjectRead:
        return await project_repository.create(session=session, project=project)

    async def get_projects(
            self,
            session: AsyncSession,
    ):
        return await project_repository.get_all(session=session)

    async def get_project_by_id(self, project_id: uuid.UUID, session: AsyncSession) -> ProjectRead:
        return await project_repository.get(session=session, id=project_id)



project_service = ProjectService()
