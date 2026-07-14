from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from app.api.users import auth_backend, fastapi_users
from app.api.routes import project_router, task_router
from app.schemas.user import UserRead, UserCreate
from app.db.session import create_db_and_tables
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="Swibit Backend Engineer Backend Test", lifespan=lifespan)

app.include_router(router=fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"])

app.include_router(router=project_router)
app.include_router(router=task_router)
