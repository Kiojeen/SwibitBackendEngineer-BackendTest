import json
import os
from datetime import datetime

from app.celery_app import celery_app
from app.db.session import get_sync_session
from app.models.export import Export
from app.models.project import Project
from app.models.task import Task

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "exports")


def _serialize(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "value"):
        return obj.value
    return str(obj)


@celery_app.task
def export_user_data(export_id: str):
    os.makedirs(EXPORT_DIR, exist_ok=True)

    session = get_sync_session()
    try:
        export = session.query(Export).filter(Export.id == export_id).first()
        if export is None:
            return

        export.status = "in_progress"
        session.commit()

        projects = session.query(Project).filter(Project.user_id == export.user_id).all()

        data = {
            "exported_at": datetime.now().isoformat(),
            "projects": [],
        }

        for project in projects:
            tasks = session.query(Task).filter(Task.project_id == project.id).all()
            project_data = {
                "id": str(project.id),
                "title": project.title,
                "user_id": str(project.user_id),
                "created_at": _serialize(project.created_at),
                "updated_at": _serialize(project.updated_at),
                "tasks": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "status": _serialize(task.status),
                        "project_id": str(task.project_id),
                        "created_at": _serialize(task.created_at),
                        "updated_at": _serialize(task.updated_at),
                    }
                    for task in tasks
                ],
            }
            data["projects"].append(project_data)

        file_name = f"export_{export_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = os.path.join(EXPORT_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        export.status = "completed"
        export.file_path = file_path
        session.commit()

    except Exception:
        session.rollback()
        export = session.query(Export).filter(Export.id == export_id).first()
        if export:
            export.status = "failed"
            session.commit()
        raise
    finally:
        session.close()
