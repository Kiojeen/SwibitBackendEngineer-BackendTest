from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.task import TaskCreate
from app.services.task_service import task_service, TaskService

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)

@router.post("/")
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_async_session)):
    return await task_service.create_task(task=task, session=session)

@router.get("/")
async def get_tasks(session: AsyncSession = Depends(get_async_session)):
    return await task_service.get_tasks(session=session)
