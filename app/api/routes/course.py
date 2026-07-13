import uuid

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.schemas.course import CourseCreate
from app.services.course_service import course_service

router = APIRouter(
    prefix="/course",
    tags=["Course"],
)


@router.post("/")
async def create_course(course: CourseCreate, session: AsyncSession = Depends(get_async_session)):
    return await course_service.create_course(session=session, course=course)


@router.get("/")
async def get_courses(session: AsyncSession = Depends(get_async_session)):
    return await course_service.get_courses(session=session)


@router.get("/{course_id}")
async def get_course_by_id(course_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    return await course_service.get_course_by_id(session=session, id=course_id)
