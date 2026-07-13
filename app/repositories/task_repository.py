import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


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

    async def get_by_id(self, task_id: uuid.UUID, session: AsyncSession) -> Task:
        result = await session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def update(self, task_id: uuid.UUID, task: TaskUpdate) -> Task:
        pass

    async def delete(self, task_id: uuid.UUID, session: AsyncSession):
        pass


task_repository = TaskRepository()
