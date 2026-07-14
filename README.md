# Swibit Backend Engineer - Backend Task

## Personal Catalog API - Task Board

A **Task Board** backend where authenticated users can create projects (lists) and manage tasks (items) within them. Designed as a technical assessment demonstrating REST API design, async Python, background job processing, and containerized deployment.

---

## Tech Stack

- **Python 3.14+**
- **FastAPI**: async web framework
- **PostgreSQL 16**: primary database
- **SQLAlchemy 2.0**: async ORM with `asyncpg` driver
- **Alembic**: schema migrations
- **Celery + Redis**: background job processing for exports
- **MinIO**: S3-compatible object storage for export files
- **Docker & Docker Compose**: full-stack containerization
- **fastapi-users**: authentication with JWT Bearer tokens

---

## Setup and Run

### Prerequisites

- Docker & Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Kiojeen/swibitbackendengineer-backendtest.git
cd swibitbackendengineer-backendtest
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your own secrets if needed. The defaults work for local development.

### 3. Start the full stack

```bash
docker compose up --build
```

This single command builds and starts all services:

| Service | Description |
|---|---|
| `db` | PostgreSQL 16 |
| `redis` | Redis 7 (Celery broker/backend) |
| `minio` | S3-compatible object storage |
| `api` | FastAPI application (port 8000) |
| `worker` | Celery worker for background exports |

The API is available at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### Database migrations

Migrations run automatically on first API startup through `Base.metadata.create_all`. To run them explicitly:

```bash
alembic upgrade head
```

If adding new models, generate a migration with:

```bash
alembic revision --autogenerate -m "description"
```

---

## Configuration & Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|---|---|---|
| `DB_USER` | PostgreSQL user | `myuser` |
| `DB_PASSWORD` | PostgreSQL password | `mysecretpassword` |
| `DB_NAME` | PostgreSQL database name | `mydatabase` |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | Secret key for JWT token signing | *(generate your own)* |
| `MINIO_ENDPOINT` | MinIO server address | `localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO access key | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO secret key | `minioadmin` |
| `MINIO_BUCKET` | MinIO bucket for export files | `exports` |
| `MINIO_SECURE` | Use HTTPS for MinIO | `false` |

---

## API Documentation

Full interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI) once the server is running.


### List Export Flow

Exporting user data is handled asynchronously. The API creates a job record and returns immediately. A Celery worker picks up the job, queries the user's projects and tasks, generates a JSON file, uploads it to MinIO, and updates the job status.

- `POST /export/` — triggers an export (returns job with status `pending`)
- `GET /export/` — list exports
- `GET /export/{id}` — check export status (`pending`, `in_progress`, `completed`, `failed`)
- `GET /export/{id}/download` — download the JSON file (available when status is `completed`)

---

## Limitations

- **Single Celery worker container.** The worker uses `--pool=prefork --concurrency=4` for parallel task processing. For higher throughput, the `--concurrency` value can be increased, or multiple worker replicas can be added to docker-compose.
- **MinIO without TLS.** The default configuration uses `MINIO_SECURE=false`. Suitable for local development; should be secured in any shared environment.
- **No rate limiting.** The API does not implement request throttling.
- **Tokens expire after 1 hour.** There is no refresh token flow; clients must re-authenticate.


## AI Tools Used

- **DeepSeek V4 Flash Free (opencode)**: Used for automating basic CRUD operations, generating tests and helped writing the README.md file.
