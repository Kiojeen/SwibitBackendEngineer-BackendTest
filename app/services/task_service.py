from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.project_repository import project_repository
from app.repositories.task_repository import task_repository


class TaskService:
    async def create_task(self, task: Task, session: AsyncSession) -> Task:
        project = await project_repository.get_by_id(project_id=task.project_id, session=session)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return await task_repository.create(task=task, session=session)

    async def get_tasks(self, session: AsyncSession) -> List[Task]:
        tasks = await task_repository.get_all(session=session)

        return tasks


task_service = TaskService()
