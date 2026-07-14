import uuid

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectPaginated, ProjectRead, ProjectUpdate
from app.services.project_service import project_service

router = APIRouter(
    prefix="/project",
    tags=["Project"],
)


@router.post("/", response_model=ProjectRead)
async def create_project(
        project: ProjectCreate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await project_service.create_project(project_data=project, user=user, session=session)


@router.get("/", response_model=ProjectPaginated)
async def get_projects(
        offset: int = 0,
        limit: int = 10,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await project_service.get_projects(user=user, session=session, offset=offset, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project_by_id(
        project_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await project_service.get_project_by_id(project_id=project_id, user=user, session=session)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
        project_id: uuid.UUID,
        project_data: ProjectUpdate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await project_service.update_project(project_id=project_id, project_data=project_data, user=user, session=session)


@router.delete("/{project_id}")
async def delete_project(
        project_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await project_service.delete_project(project_id=project_id, user=user, session=session)
