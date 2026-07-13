import uuid

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.project import ProjectCreate
from app.services.project_service import project_service

router = APIRouter(
    prefix="/project",
    tags=["Project"],
)


@router.post("/")
async def create_project(project: ProjectCreate, session: AsyncSession = Depends(get_async_session)):
    return await project_service.create_project(session=session, project=project)


@router.get("/")
async def get_projects(session: AsyncSession = Depends(get_async_session)):
    return await project_service.get_projects(session=session)


@router.get("/{project_id}")
async def get_project_by_id(project_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await project_service.get_project_by_id(project_id=project_id, session=session)

@router.post("/")
async def update_project(project: ProjectCreate, session: AsyncSession = Depends(get_async_session)):
    pass
