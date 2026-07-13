import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.course_repository import course_repository
from app.schemas.course import CourseCreate, CourseRead


class CourseService:
    async def create_course(self, course: CourseCreate, session: AsyncSession) -> CourseRead:
        return await course_repository.create(session=session, course=course)

    async def get_courses(
            self,
            session: AsyncSession,
    ):
        return await course_repository.get_all(session=session)

    async def get_course_by_id(self, course_id: uuid.UUID, session: AsyncSession) -> CourseRead:
        return await course_repository.get(session=session, id=course_id)



course_service = CourseService()
