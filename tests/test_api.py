"""Automated integration tests covering four required categories:

1. Registration / Authentication
2. Cross-user authorization isolation
3. Invalid input / database constraints
4. Export lifecycle
"""

import uuid
from unittest.mock import patch

from app.tasks.user_tasks import export_user_data


# ---------------------------------------------------------------------------
# 1. Registration / Authentication
# ---------------------------------------------------------------------------

class TestAuth:
    def test_login_succeeds_with_valid_credentials(self, client, unique_email, password):
        """Register a new user, then log in — expect a JWT token back."""
        register_resp = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password},
        )
        assert register_resp.status_code == 201
        assert register_resp.json()["email"] == unique_email

        login_resp = client.post(
            "/auth/jwt/login",
            data={"username": unique_email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_resp.status_code == 200
        body = login_resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"


# ---------------------------------------------------------------------------
# 2. Cross-user authorization isolation
# ---------------------------------------------------------------------------

class TestAuthorization:
    def test_user_b_cannot_access_user_a_project(self, client, user_a, user_b, project_a):
        """User B receives 403 when trying to read User A's project."""
        resp = client.get(
            f"/project/{project_a['id']}",
            headers={"Authorization": f"Bearer {user_b['token']}"},
        )
        assert resp.status_code == 403
        assert "Not authorized" in resp.json()["detail"]

    def test_user_b_cannot_delete_user_a_project(self, client, user_a, user_b, project_a):
        resp = client.delete(
            f"/project/{project_a['id']}",
            headers={"Authorization": f"Bearer {user_b['token']}"},
        )
        assert resp.status_code == 403

    def test_user_b_cannot_create_task_in_user_a_project(self, client, user_a, user_b, project_a):
        resp = client.post(
            "/task/",
            json={"title": "Hacked task", "project_id": project_a["id"]},
            headers={"Authorization": f"Bearer {user_b['token']}"},
        )
        assert resp.status_code == 403

    def test_user_b_sees_only_own_exports(self, client, user_a, user_b):
        with patch("app.tasks.user_tasks.export_user_data.delay"):
            client.post(
                "/export/",
                headers={"Authorization": f"Bearer {user_a['token']}"},
            )
        resp = client.get(
            "/export/",
            headers={"Authorization": f"Bearer {user_b['token']}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 0


# ---------------------------------------------------------------------------
# 3. Invalid input / database constraints
# ---------------------------------------------------------------------------

class TestValidation:
    def test_create_project_missing_title_returns_422(self, client, user_a):
        resp = client.post(
            "/project/",
            json={},
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert resp.status_code == 422

    def test_register_duplicate_email_returns_400(self, client, unique_email, password):
        client.post("/auth/register", json={"email": unique_email, "password": password})
        resp = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password},
        )
        assert resp.status_code == 400
        assert "ALREADY_EXISTS" in resp.json()["detail"]

    def test_create_task_invalid_uuid_returns_422(self, client, user_a):
        resp = client.post(
            "/task/",
            json={"title": "Bad task", "project_id": "not-a-uuid"},
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert resp.status_code == 422

    def test_create_task_invalid_status_returns_422(self, client, user_a, project_a):
        resp = client.post(
            "/task/",
            json={
                "title": "Bad status",
                "project_id": project_a["id"],
                "status": "invalid_status",
            },
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert resp.status_code == 422

    def test_create_task_nonexistent_project_returns_404(self, client, user_a):
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = client.post(
            "/task/",
            json={"title": "Orphan task", "project_id": fake_id},
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 4. Export lifecycle
# ---------------------------------------------------------------------------

class TestExport:
    def test_export_created_with_pending_status(self, client, user_a, project_a):
        """POST /export/ returns a job with status='pending'."""
        with patch("app.tasks.user_tasks.export_user_data.delay") as mock_delay:
            mock_delay.return_value = None
            resp = client.post(
                "/export/",
                headers={"Authorization": f"Bearer {user_a['token']}"},
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "pending"
        assert body["file_path"] is None
        assert "id" in body

    def test_export_status_transitions_to_completed(self, client, user_a, project_a):
        """After the background job runs, status becomes 'completed' and the
        download endpoint serves a file."""
        with patch("app.tasks.user_tasks.export_user_data.delay"):
            create_resp = client.post(
                "/export/",
                headers={"Authorization": f"Bearer {user_a['token']}"},
            )
        export_id = create_resp.json()["id"]

        # Simulate the worker by calling the task directly
        export_user_data(str(export_id))

        # Check status is now completed
        status_resp = client.get(
            f"/export/{export_id}",
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "completed"
        assert status_resp.json()["file_path"] is not None

        # Download the file
        download_resp = client.get(
            f"/export/{export_id}/download",
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert download_resp.status_code == 200
        assert download_resp.headers["content-type"] == "application/json"

    def test_download_before_completion_returns_404(self, client, user_a):
        with patch("app.tasks.user_tasks.export_user_data.delay"):
            create_resp = client.post(
                "/export/",
                headers={"Authorization": f"Bearer {user_a['token']}"},
            )
        export_id = create_resp.json()["id"]

        # Download while still pending
        download_resp = client.get(
            f"/export/{export_id}/download",
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert download_resp.status_code == 404

    def test_export_nonexistent_returns_404(self, client, user_a):
        fake_id = uuid.uuid4()
        resp = client.get(
            f"/export/{fake_id}",
            headers={"Authorization": f"Bearer {user_a['token']}"},
        )
        assert resp.status_code == 404
