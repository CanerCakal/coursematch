from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.course import Course
from app.models.department import Department
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
):
    department = (
        db.query(Department)
        .filter(Department.id == course_data.department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Bölüm bulunamadı.",
        )

    course = Course(**course_data.model_dump())

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.get("/", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.name).all()


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Ders bulunamadı.",
        )

    return course


@router.put("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Ders bulunamadı.",
        )

    update_data = course_data.model_dump(exclude_unset=True)

    if "department_id" in update_data:
        department = (
            db.query(Department)
            .filter(Department.id == update_data["department_id"])
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=404,
                detail="Bölüm bulunamadı.",
            )

    for field, value in update_data.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)

    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
):
    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Ders bulunamadı.",
        )

    db.delete(course)
    db.commit()

    return None