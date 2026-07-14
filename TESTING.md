# Manual Test Cases

This document covers manual testing for all normal flows and robustness cases.  
All tests assume the API is running at `http://localhost:8000`.

---

## Setup

```bash
# Register two users for isolation tests
USER_A_EMAIL="alice@test.com"
USER_A_PASS="password123"
USER_B_EMAIL="bob@test.com"
USER_B_PASS="password456"

# Register Alice
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$USER_A_EMAIL\",\"password\":\"$USER_A_PASS\"}"

# Register Bob
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$USER_B_EMAIL\",\"password\":\"$USER_B_PASS\"}"

# Login as Alice and capture token
TOKEN_A=$(curl -s -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USER_A_EMAIL&password=$USER_A_PASS" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Login as Bob and capture token
TOKEN_B=$(curl -s -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USER_B_EMAIL&password=$USER_B_PASS" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

## Normal Flows

### TC-01: Registration

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /auth/register` | `{"email": "newuser@test.com", "password": "pass123"}` | `201` — JSON with `id`, `email`, `is_active: true` |
| 2 | Repeat same email | same body | `400` — `{"detail": "REGISTER_USER_ALREADY_EXISTS"}` |

### TC-02: Login

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /auth/jwt/login` | Form: `username=newuser@test.com`, `password=pass123` | `200` — `{"access_token": "...", "token_type": "bearer"}` |
| 2 | Wrong password | `username=newuser@test.com`, `password=wrong` | `400` — `{"detail": "LOGIN_BAD_CREDENTIALS"}` |

### TC-03: Create and List Projects

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /project/` (Alice) | `{"title": "Sprint 1"}` | `201` — project object with `id`, `title`, `created_at` |
| 2 | `POST /project/` (Alice) | `{"title": "Sprint 2"}` | `201` — second project created |
| 3 | `GET /project/?offset=0&limit=10` (Alice) | — | `200` — `{"items": [...2 items], "total": 2, "offset": 0, "limit": 10}` |
| 4 | `GET /project/?offset=0&limit=1` (Alice) | — | `200` — `{"items": [...1 item], "total": 2, "offset": 0, "limit": 1}` |

### TC-04: Update and Delete Project

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `PATCH /project/{id}` (Alice) | `{"title": "Updated Sprint"}` | `200` — project with updated `title` |
| 2 | `GET /project/{id}` (Alice) | — | `200` — updated title confirmed |
| 3 | `DELETE /project/{id}` (Alice) | — | `204` — no content |
| 4 | `GET /project/{id}` (Alice) | — | `404` — `{"detail": "Project not found."}` |

### TC-05: Create, List, Update, Delete Tasks

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /project/` (Alice) | `{"title": "My Project"}` | `201` — save `PROJECT_ID` |
| 2 | `POST /task/` (Alice) | `{"title": "Task 1", "project_id": "$PROJECT_ID"}` | `201` — task with `id`, `title`, `status: "pending"` |
| 3 | `POST /task/` (Alice) | `{"title": "Task 2", "project_id": "$PROJECT_ID", "status": "in_progress"}` | `201` — task with `status: "in_progress"` |
| 4 | `GET /task/?offset=0&limit=10` (Alice) | — | `200` — `{"items": [...2 tasks], "total": 2}` |
| 5 | `PATCH /task/{id}` (Alice) | `{"status": "completed"}` | `200` — task status updated |
| 6 | `DELETE /task/{id}` (Alice) | — | `204` |
| 7 | `GET /task/{id}` (Alice) | — | `404` |

### TC-06: Export Flow

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /export/` (Alice) | — | `201` — export object with `status: "pending"`, `id` |
| 2 | `GET /export/{id}` (Alice) | — | `200` — status is `"pending"` or `"in_progress"` or `"completed"` |
| 3 | Wait for Celery worker to process (a few seconds) | — | — |
| 4 | `GET /export/{id}` (Alice) | — | `200` — `status: "completed"`, `file_path: "exports/{id}.json"` |
| 5 | `GET /export/{id}/download` (Alice) | — | `200` — JSON file with `exported_at`, `projects` array containing all Alice's data |
| 6 | `GET /export/` (Alice) | — | `200` — `{"items": [...1 export], "total": 1}` |

---

## Robustness Cases

### RC-01: Unauthenticated Access

Accessing any protected endpoint without a Bearer token.

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `GET /project/` | No `Authorization` header | `401` — `{"detail": "Unauthorized"}` |
| 2 | `POST /project/` | No `Authorization` header, `{"title": "x"}` | `401` — `{"detail": "Unauthorized"}` |
| 3 | `GET /task/` | No `Authorization` header | `401` — `{"detail": "Unauthorized"}` |
| 4 | `POST /task/` | No `Authorization` header, `{"title": "x", "project_id": "..."}` | `401` — `{"detail": "Unauthorized"}` |
| 5 | `POST /export/` | No `Authorization` header | `401` — `{"detail": "Unauthorized"}` |
| 6 | `GET /export/{id}/download` | No `Authorization` header | `401` — `{"detail": "Unauthorized"}` |

### RC-02: Cross-User Resource Access

User B attempts to access, modify, or delete User A's resources.

**Setup**: Alice has a project (`PROJECT_ID_A`) with a task (`TASK_ID_A`). Bob has his own project.

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `GET /project/{PROJECT_ID_A}` (Bob's token) | — | `403` — `{"detail": "Not authorized to access this project."}` |
| 2 | `PATCH /project/{PROJECT_ID_A}` (Bob's token) | `{"title": "hacked"}` | `403` — `{"detail": "Not authorized to update this project."}` |
| 3 | `DELETE /project/{PROJECT_ID_A}` (Bob's token) | — | `403` — `{"detail": "Not authorized to delete this project."}` |
| 4 | `GET /task/{TASK_ID_A}` (Bob's token) | — | `403` — `{"detail": "Not authorized to access this task."}` |
| 5 | `PATCH /task/{TASK_ID_A}` (Bob's token) | `{"status": "completed"}` | `403` — `{"detail": "Not authorized to update this task."}` |
| 6 | `DELETE /task/{TASK_ID_A}` (Bob's token) | — | `403` — `{"detail": "Not authorized to delete this task."}` |
| 7 | `GET /export/` (Bob's token) | — | `200` — Bob sees only his exports, not Alice's |

### RC-03: Non-Existent Resource

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `GET /project/{non-existent-uuid}` (Alice) | UUID with no matching record | `404` — `{"detail": "Project not found."}` |
| 2 | `PATCH /project/{non-existent-uuid}` (Alice) | `{"title": "x"}` | `404` — `{"detail": "Project not found."}` |
| 3 | `DELETE /project/{non-existent-uuid}` (Alice) | — | `404` — `{"detail": "Project not found."}` |
| 4 | `GET /task/{non-existent-uuid}` (Alice) | — | `404` — `{"detail": "Task not found."}` |
| 5 | `PATCH /task/{non-existent-uuid}` (Alice) | `{"title": "x"}` | `404` — `{"detail": "Task not found."}` |
| 6 | `DELETE /task/{non-existent-uuid}` (Alice) | — | `404` — `{"detail": "Task not found."}` |
| 7 | `GET /export/{non-existent-uuid}` (Alice) | — | `404` — `{"detail": "Export not found."}` |
| 8 | `GET /export/{non-existent-uuid}/download` (Alice) | — | `404` — `{"detail": "Export not found."}` |

### RC-04: Invalid Input / Validation Errors

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /project/` (Alice) | `{}` (empty body) | `422` — validation error for missing `title` |
| 2 | `POST /project/` (Alice) | `{"title": null}` | `422` — `title` must be a string |
| 3 | `POST /task/` (Alice) | `{"title": "x"}` (missing `project_id`) | `422` — `project_id` field required |
| 4 | `POST /task/` (Alice) | `{"title": "x", "project_id": "not-a-uuid"}` | `422` — invalid UUID format |
| 5 | `POST /task/` (Alice) | `{"title": "x", "project_id": "$PROJECT_ID", "status": "invalid_status"}` | `422` — invalid enum value |
| 6 | `PATCH /task/{id}` (Alice) | `{"status": "invalid"}` | `422` — invalid enum value |

### RC-05: Operations on Non-Existent or Foreign Parent

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `POST /task/` (Alice) | `{"title": "x", "project_id": "$NON_EXISTENT_UUID"}` | `404` — `{"detail": "Project not found."}` |
| 2 | `POST /task/` (Alice) | `{"title": "x", "project_id": "$BOBS_PROJECT_ID"}` | `403` — `{"detail": "Not authorized to access this project."}` |
| 3 | Delete the project that contains tasks | `DELETE /project/{id}` where project has tasks | `204` — cascade deletes tasks (verify with `GET /task/`) |

### RC-06: Export State Management

| Step | Action | Input | Expected Output |
|---|---|---|---|
| 1 | `GET /export/{id}/download` (Alice) when export is `pending` | Export just created, not yet processed | `404` — `{"detail": "Export file not available."}` |
| 2 | `GET /export/{id}/download` (Alice) when export is `failed` | Export that failed (e.g., stop Celery, trigger export, check) | `404` — `{"detail": "Export file not available."}` |
| 3 | `GET /export/{id}/download` (Alice) with non-existent export ID | — | `404` — `{"detail": "Export not found."}` |
| 4 | `GET /export/{id}/download` (Bob) for Alice's completed export | Use Alice's export ID with Bob's token | `403` — `{"detail": "Not authorized to access this export."}` |
| 5 | Trigger multiple exports | `POST /export/` three times | `201` each — all return `status: "pending"` with unique IDs |
| 6 | Paginate exports | `GET /export/?offset=0&limit=2` (Alice) | `200` — `{"items": [...], "total": 3, "offset": 0, "limit": 2}` |

---

## Automated Tests (pytest)

14 integration tests covering four required categories. Tests run against the real database (PostgreSQL must be available) using `TestClient` with ASGI transport — no server process needed.

### Run

```bash
# From the repo root, with services (postgres, redis, minio) running
uv run pytest tests/ -v
```

### Coverage

| Category | Tests | What it covers |
|---|---|---|
| **Auth / Registration** | `TestAuth` (1 test) | Register + login flow, JWT token returned with `token_type: "bearer"` |
| **Cross-user authorization** | `TestAuthorization` (4 tests) | User B receives `403` when reading/deleting/creating tasks in User A's project; User B sees zero exports from User A |
| **Invalid input / constraints** | `TestValidation` (5 tests) | `422` for missing title, invalid UUID, invalid enum status; `400` for duplicate email; `404` for non-existent parent project |
| **Export lifecycle** | `TestExport` (4 tests) | Export created with `status: "pending"`; status transitions to `"completed"` after worker task runs (called synchronously via patched `delay`); `404` if downloaded before completion or with non-existent ID |

### Notes

- Each test generates unique email addresses (`uuid` suffix) to avoid collisions with existing data.
- The export Celery task is tested by patching `.delay()` and calling the task function directly — no Celery worker required.
- The `client` fixture is session-scoped (lifespan runs once).