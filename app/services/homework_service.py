from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.homework import Homework
from app.repositories.course_repository import course_repository
from app.repositories.homework_repository import homework_repository


class HomeworkService:
    async def create_homework(self, homework: Homework, session: AsyncSession) -> Homework:
        course = await course_repository.get_by_id(session=session, course_id=homework.course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found.",
            )

        return await homework_repository.create(homework=homework, session=session)

    async def get_homeworks(self, session: AsyncSession) -> List[Homework]:
        homeworks = await homework_repository.get_all(session=session)

        return homeworks


homework_service = HomeworkService()
