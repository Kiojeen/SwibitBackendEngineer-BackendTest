from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str


class CourseRead(BaseModel):
    title: str
