from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CourseComparison(Base):
    __tablename__ = "course_comparisons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    source_course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        nullable=False,
        index=True,
    )
    target_course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        nullable=False,
        index=True,
    )

    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    keyword_similarity_score: Mapped[float] = mapped_column(Float, nullable=False)

    ects_match: Mapped[bool] = mapped_column(Boolean, nullable=False)
    credit_match: Mapped[bool] = mapped_column(Boolean, nullable=False)

    matched_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    source_course = relationship(
        "Course",
        foreign_keys=[source_course_id],
    )
    target_course = relationship(
        "Course",
        foreign_keys=[target_course_id],
    )