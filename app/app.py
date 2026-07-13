from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import create_db_and_tables, get_async_session
from app.models.course import Course
from app.schemas.course import CourseCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="Swibit Backend Engineer Backend Test", lifespan=lifespan)


@app.post("/course")
async def add_course(course: CourseCreate, session: AsyncSession = Depends(get_async_session)):
    course = Course(
        title=course.title,
    )

    session.add(course)
    await session.commit()
    await session.refresh(course)

    return course


@app.get("/course")
async def get_courses(session: AsyncSession = Depends(get_async_session)):
    courses = await session.execute(select(Course).order_by(Course.title))

    return {
        "courses": [course.title for course in courses.scalars().all()]
    }
