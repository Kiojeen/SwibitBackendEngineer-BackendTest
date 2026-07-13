from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.schemas.course import CourseCreate


class CourseRepository:
    async def create(self, session: AsyncSession, course: CourseCreate) -> Course:
        course = Course(
            title=course.title,
        )

        session.add(course)
        await session.commit()
        await session.refresh(course)

        return course

    async def get_all(self, session: AsyncSession):
        courses = await session.execute(select(Course).order_by(Course.title))

        return courses.scalars().all()


course_repository = CourseRepository()
