import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import current_active_user
from app.db.session import get_async_session
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPaginated, TaskRead, TaskUpdate
from app.services.task_service import task_service

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)

@router.post("/", response_model=TaskRead)
async def create_task(
        task: TaskCreate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await task_service.create_task(task_data=task, user=user, session=session)

@router.get("/", response_model=TaskPaginated)
async def get_tasks(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
        offset: int = 0,
        limit: int = 10,
):
    return await task_service.get_tasks(user=user, session=session, offset=offset, limit=limit)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task_by_id(
        task_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await task_service.get_task_by_id(task_id=task_id, user=user, session=session)

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
        task_id: uuid.UUID,
        task_data: TaskUpdate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await task_service.update_task(task_id=task_id, task_data=task_data, user=user, session=session)

@router.delete("/{task_id}")
async def delete_task(
        task_id: uuid.UUID,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await task_service.delete_task(task_id=task_id, user=user, session=session)

