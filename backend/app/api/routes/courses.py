import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.course import Course
from app.models.course_comparison import CourseComparison
from app.models.department import Department
from app.schemas.course import (
    CourseCompareRequest,
    CourseCompareResponse,
    CourseComparisonHistoryItem,
    CourseCreate,
    CourseRead,
    CourseUpdate,
)
from app.services.course_similarity import calculate_course_similarity

router = APIRouter(prefix="/courses", tags=["Courses"])

def build_comparison_history_item(
    comparison: CourseComparison,
) -> CourseComparisonHistoryItem:
    return CourseComparisonHistoryItem(
        id=comparison.id,
        source_course_id=comparison.source_course_id,
        source_course_name=comparison.source_course.name,
        target_course_id=comparison.target_course_id,
        target_course_name=comparison.target_course.name,
        similarity_score=comparison.similarity_score,
        keyword_similarity_score=comparison.keyword_similarity_score,
        ects_match=comparison.ects_match,
        credit_match=comparison.credit_match,
        matched_keywords=json.loads(comparison.matched_keywords or "[]"),
        recommendation=comparison.recommendation,
        summary=comparison.summary,
        created_at=comparison.created_at,
    )


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


@router.post("/compare", response_model=CourseCompareResponse)
def compare_courses(
    compare_data: CourseCompareRequest,
    db: Session = Depends(get_db),
):
    if compare_data.source_course_id == compare_data.target_course_id:
        raise HTTPException(
            status_code=400,
            detail="Bir ders kendisiyle karşılaştırılamaz.",
        )

    source_course = (
        db.query(Course)
        .filter(Course.id == compare_data.source_course_id)
        .first()
    )

    if not source_course:
        raise HTTPException(
            status_code=404,
            detail="Kaynak ders bulunamadı.",
        )

    target_course = (
        db.query(Course)
        .filter(Course.id == compare_data.target_course_id)
        .first()
    )

    if not target_course:
        raise HTTPException(
            status_code=404,
            detail="Hedef ders bulunamadı.",
        )

    comparison_result = calculate_course_similarity(source_course, target_course)

    comparison = CourseComparison(
        source_course_id=comparison_result["source_course_id"],
        target_course_id=comparison_result["target_course_id"],
        similarity_score=comparison_result["similarity_score"],
        keyword_similarity_score=comparison_result["keyword_similarity_score"],
        ects_match=comparison_result["ects_match"],
        credit_match=comparison_result["credit_match"],
        matched_keywords=json.dumps(
            comparison_result["matched_keywords"],
            ensure_ascii=False,
        ),
        recommendation=comparison_result["recommendation"],
        summary=comparison_result["summary"],
    )

    db.add(comparison)
    db.commit()

    return comparison_result

@router.get("/comparisons", response_model=list[CourseComparisonHistoryItem])
def list_course_comparisons(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    comparisons = (
        db.query(CourseComparison)
        .order_by(CourseComparison.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        build_comparison_history_item(comparison)
        for comparison in comparisons
    ]

@router.delete("/comparisons/{comparison_id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_course_comparison(
    comparison_id: int,
    db: Session = Depends(get_db),
):
    comparison = (
        db.query(CourseComparison)
        .filter(CourseComparison.id == comparison_id)
        .first()
    )

    if not comparison:
        raise HTTPException(
            status_code=404,
            detail="Karşılaştırma kaydı bulunamadı.",
        )

    db.delete(comparison)
    db.commit()

    return None

@router.get("/{course_id}/comparisons",response_model=list[CourseComparisonHistoryItem],)
def list_comparisons_for_course(
    course_id: int,
    limit: int = 20,
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

    comparisons = (
        db.query(CourseComparison)
        .filter(
            or_(
                CourseComparison.source_course_id == course_id,
                CourseComparison.target_course_id == course_id,
            )
        )
        .order_by(CourseComparison.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        build_comparison_history_item(comparison)
        for comparison in comparisons
    ]

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