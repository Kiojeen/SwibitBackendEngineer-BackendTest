from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.course_repository import course_repository
from app.schemas.course import CourseCreate


class CourseService:
    async def create_course(self, session: AsyncSession, course: CourseCreate) -> Course:
        return await course_repository.create(session=session, course=course)

    async def get_courses(
            self,
            session: AsyncSession,
    ):
        return await course_repository.get_all(session=session)


course_service = CourseService()
