from pydantic import BaseModel


class CourseBase(BaseModel):
    department_id: int
    code: str | None = None
    name: str
    language: str | None = None
    ects: int | None = None
    credit: int | None = None
    description: str | None = None
    weekly_plan: str | None = None
    learning_outcomes: str | None = None
    resources: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    department_id: int | None = None
    code: str | None = None
    name: str | None = None
    language: str | None = None
    ects: int | None = None
    credit: int | None = None
    description: str | None = None
    weekly_plan: str | None = None
    learning_outcomes: str | None = None
    resources: str | None = None


class CourseRead(CourseBase):
    id: int

    class Config:
        from_attributes = True