import uuid

from fastapi.testclient import TestClient

import pytest

from app.app import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@test.com"


@pytest.fixture
def password():
    return "testpass123"


def register_and_login(client, email: str, password: str):
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


@pytest.fixture
def user_a(client, unique_email, password):
    token = register_and_login(client, unique_email, password)
    return {"email": unique_email, "password": password, "token": token}


@pytest.fixture
def user_b(client, unique_email, password):
    token = register_and_login(client, f"b-{unique_email}", password)
    return {"email": f"b-{unique_email}", "password": password, "token": token}


@pytest.fixture
def project_a(client, user_a):
    resp = client.post(
        "/project/",
        json={"title": "Test Project"},
        headers={"Authorization": f"Bearer {user_a['token']}"},
    )
    return resp.json()
