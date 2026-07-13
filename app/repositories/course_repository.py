import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.schemas.course import CourseCreate


class CourseRepository:
    async def create(self, course: CourseCreate, session: AsyncSession) -> Course:
        course_db = Course(
            title=course.title,
        )

        session.add(course_db)
        await session.commit()
        await session.refresh(course_db)

        return course_db

    async def get_all(self, session: AsyncSession):
        courses = await session.execute(select(Course).order_by(Course.title))

        return courses.scalars().all()

    async def get_by_id(self, session: AsyncSession, course_id: uuid.UUID) -> Course:
        course = await session.execute(select(Course).where(Course.id == course_id))
        return course.scalar_one_or_none()


course_repository = CourseRepository()
