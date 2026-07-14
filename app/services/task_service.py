import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user import User
from app.repositories.project_repository import project_repository
from app.repositories.task_repository import task_repository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    async def create_task(self, task_data: TaskCreate, user: User, session: AsyncSession) -> Task:
        project = await project_repository.get_by_id(project_id=task_data.project_id, session=session)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found.")

        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this project.")

        task = Task(title=task_data.title, project_id=task_data.project_id, status=task_data.status)
        return await task_repository.create(task=task, session=session)

    async def get_tasks(self, user: User, session: AsyncSession, offset: int = 0, limit: int = 10) -> List[Task]:
        return await task_repository.get_by_user_id(user_id=user.id, session=session, offset=offset, limit=limit)

    async def get_task_by_id(self, task_id: uuid.UUID, user: User, session: AsyncSession) -> Task:
        task = await task_repository.get_by_id(task_id=task_id, session=session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        project = await project_repository.get_by_id(project_id=task.project_id, session=session)
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this task.")
        return task

    async def update_task(self, task_id: uuid.UUID, task_data: TaskUpdate, user: User, session: AsyncSession) -> Task:
        task = await task_repository.get_by_id(task_id=task_id, session=session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        project = await project_repository.get_by_id(project_id=task.project_id, session=session)
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this task.")
        updated = await task_repository.update(task_id=task_id, task_data=task_data, session=session)
        if updated is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return updated

    async def delete_task(self, task_id: uuid.UUID, user: User, session: AsyncSession) -> bool:
        task = await task_repository.get_by_id(task_id=task_id, session=session)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        project = await project_repository.get_by_id(project_id=task.project_id, session=session)
        if project.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this task.")
        return await task_repository.delete(task_id=task_id, session=session)


task_service = TaskService()
