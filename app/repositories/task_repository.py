import uuid
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskUpdate


class TaskRepository:

    async def create(self, task: Task, session: AsyncSession) -> Task:
        session.add(task)

        await session.commit()
        await session.refresh(task)
        return task

    async def get_by_user_id(self, user_id: uuid.UUID, session: AsyncSession, offset: int = 0, limit: int = 10) -> List[
        Task]:
        result = await session.execute(
            select(Task).join(Task.project).where(
                Task.project.has(user_id=user_id)
            ).order_by(Task.title).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_user_id(self, user_id: uuid.UUID, session: AsyncSession) -> int:
        result = await session.execute(
            select(func.count()).select_from(Task).join(Task.project).where(
                Task.project.has(user_id=user_id)
            )
        )
        return result.scalar_one()

    async def get_by_id(self, task_id: uuid.UUID, session: AsyncSession) -> Task:
        result = await session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def update(self, task_id: uuid.UUID, task_data: TaskUpdate, session: AsyncSession) -> Task | None:
        task = await self.get_by_id(task_id=task_id, session=session)
        if task is None:
            return None
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.status is not None:
            task.status = task_data.status
        await session.commit()
        await session.refresh(task)
        return task

    async def delete(self, task_id: uuid.UUID, session: AsyncSession) -> bool:
        task = await self.get_by_id(task_id=task_id, session=session)
        if task is None:
            return False
        await session.delete(task)
        await session.commit()
        return True


task_repository = TaskRepository()
