from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.homework import Homework
from app.schemas.homework import HomeworkCreate


class HomeworkRepository:

    async def create(self, homework: HomeworkCreate, session: AsyncSession) -> Homework:
        homework_db = Homework(
            title=homework.title,
            course_id=homework.course_id,
        )

        session.add(homework_db)

        await session.commit()
        await session.refresh(homework_db)
        return homework_db

    async def get_all(self, session: AsyncSession) -> List[Homework]:
        result = await session.execute(select(Homework).order_by(Homework.title))

        return result.scalars().all()


homework_repository = HomeworkRepository()
