from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.homework import HomeworkCreate
from app.services.homework_service import homework_service, HomeworkService

router = APIRouter(
    prefix="/homework",
    tags=["Homework"],
)

@router.post("/")
async def create_homework(homework: HomeworkCreate,session: AsyncSession = Depends(get_async_session)):
    return await homework_service.create_homework(homework=homework, session=session)

@router.get("/")
async def get_homeworks(session: AsyncSession = Depends(get_async_session)):
    return await homework_service.get_homeworks(session=session)
