from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskRepository:

    async def create(self, task: TaskCreate, session: AsyncSession) -> Task:
        task_db = Task(
            title=task.title,
            project_id=task.project_id,
        )

        session.add(task_db)

        await session.commit()
        await session.refresh(task_db)
        return task_db

    async def get_all(self, session: AsyncSession) -> List[Task]:
        result = await session.execute(select(Task).order_by(Task.title))

        return result.scalars().all()


task_repository = TaskRepository()
