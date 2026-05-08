from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    university_id: Mapped[int] = mapped_column(
        ForeignKey("universities.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    faculty: Mapped[str | None] = mapped_column(String(255), nullable=True)

    university = relationship(
        "University",
        back_populates="departments",
    )

    courses = relationship(
        "Course",
        back_populates="department",
        cascade="all, delete-orphan",
    )