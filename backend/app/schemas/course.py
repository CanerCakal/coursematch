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


class CourseCompareRequest(BaseModel):
    source_course_id: int
    target_course_id: int


class CourseCompareResponse(BaseModel):
    source_course_id: int
    source_course_name: str
    target_course_id: int
    target_course_name: str
    similarity_score: float
    keyword_similarity_score: float
    ects_match: bool
    credit_match: bool
    matched_keywords: list[str]
    recommendation: str
    summary: str