from dotenv import load_dotenv
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.rate_limit import limiter

load_dotenv()

from contextlib import asynccontextmanager
from app.api.users import auth_backend, fastapi_users
from app.api.routes import export_router, project_router, task_router
from app.schemas.user import UserRead, UserCreate
from fastapi import FastAPI

import app.tasks.user_tasks


app = FastAPI(title="Swibit Backend Engineer Backend Test")

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)

app.include_router(router=fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"])

app.include_router(router=export_router)
app.include_router(router=project_router)
app.include_router(router=task_router)
