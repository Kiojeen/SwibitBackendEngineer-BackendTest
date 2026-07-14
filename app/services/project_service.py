import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectPaginated


class ProjectService:
    async def create_project(self, project_data: ProjectCreate, user: User, session: AsyncSession) -> ProjectRead:
        project = Project(
            title=project_data.title,
            user_id=user.id,
        )
        return await project_repository.create(project=project, session=session)

    async def get_projects(self, user: User, session: AsyncSession, offset: int = 0, limit: int = 10) -> ProjectPaginated:
        items = await project_repository.get_by_user_id(user_id=user.id, session=session, offset=offset, limit=limit)
        total = await project_repository.count_by_user_id(user_id=user.id, session=session)
        return ProjectPaginated(items=items, total=total, offset=offset, limit=limit)

    async def get_project_by_id(self, project_id: uuid.UUID, user: User, session: AsyncSession) -> Project:
        project = await project_repository.get_by_id(project_id=project_id, session=session)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found.")
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this project.")
        return project

    async def update_project(self, project_id: uuid.UUID, project_data: ProjectUpdate, user: User, session: AsyncSession) -> Project:
        project = await project_repository.get_by_id(project_id=project_id, session=session)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found.")
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this project.")
        updated = await project_repository.update(project_id=project_id, project_data=project_data, session=session)
        return updated

    async def delete_project(self, project_id: uuid.UUID, user: User, session: AsyncSession) -> bool:
        project = await project_repository.get_by_id(project_id=project_id, session=session)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found.")
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this project.")
        return await project_repository.delete(project_id=project_id, session=session)


project_service = ProjectService()
