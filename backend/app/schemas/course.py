from datetime import datetime

from pydantic import BaseModel, Field


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


class CourseListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[CourseRead]


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


class CourseRecommendationRequest(BaseModel):
    source_course_id: int
    target_department_id: int
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Dönecek maksimum öneri sayısı",
    )


class CourseRecommendationResponse(BaseModel):
    source_course_id: int
    source_course_name: str
    target_department_id: int
    total_candidates: int
    limit: int
    items: list[CourseCompareResponse]


class CourseComparisonHistoryItem(BaseModel):
    id: int
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
    created_at: datetime


class CourseComparisonHistoryResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[CourseComparisonHistoryItem]