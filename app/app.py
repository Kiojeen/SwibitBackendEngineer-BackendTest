from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.db.session import create_db_and_tables
from app.api.routes import course_router, homework_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="Swibit Backend Engineer Backend Test", lifespan=lifespan)

app.include_router(router=course_router)
app.include_router(router=homework_router)
