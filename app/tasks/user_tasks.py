import json
from datetime import datetime
from io import BytesIO

from app.celery_app import celery_app
from app.db.session import get_sync_session
from app.minio_client import MINIO_BUCKET, ensure_bucket, minio_client
from app.models.export import Export
from app.models.project import Project
from app.models.task import Task


@celery_app.task
def export_user_data(export_id: str):
    ensure_bucket()

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
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "tasks": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "status": task.status,
                        "project_id": str(task.project_id),
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat(),
                    }
                    for task in tasks
                ],
            }
            data["projects"].append(project_data)

        content = json.dumps(data, indent=2).encode("utf-8")
        object_key = f"exports/{export_id}.json"

        minio_client.put_object(
            MINIO_BUCKET,
            object_key,
            BytesIO(content),
            len(content),
            content_type="application/json",
        )

        export.status = "completed"
        export.file_path = object_key
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
