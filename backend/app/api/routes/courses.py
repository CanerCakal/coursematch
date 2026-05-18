import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    CourseComparisonHistoryResponse,
    CourseCreate,
    CourseListResponse,
    CourseRead,
    CourseRecommendationRequest,
    CourseRecommendationResponse,
    CourseUpdate,
)
from app.services.course_similarity import calculate_course_similarity

router = APIRouter(prefix="/courses", tags=["Courses"])


def build_comparison_history_item(
    comparison: CourseComparison,
) -> CourseComparisonHistoryItem:
    source_course = comparison.source_course
    target_course = comparison.target_course

    source_department = source_course.department if source_course else None
    target_department = target_course.department if target_course else None

    source_university = (
        source_department.university
        if source_department and source_department.university
        else None
    )
    target_university = (
        target_department.university
        if target_department and target_department.university
        else None
    )

    return CourseComparisonHistoryItem(
        id=comparison.id,
        source_course_id=comparison.source_course_id,
        source_course_name=source_course.name,
        source_department_name=source_department.name if source_department else None,
        source_university_name=source_university.name if source_university else None,
        target_course_id=comparison.target_course_id,
        target_course_name=target_course.name,
        target_department_name=target_department.name if target_department else None,
        target_university_name=target_university.name if target_university else None,
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


@router.get("/", response_model=CourseListResponse)
def list_courses(
    department_id: int | None = Query(
        None,
        description="Belirli bir bölüme ait dersleri filtreler",
    ),
    search: str | None = Query(
        None,
        description="Ders adı veya ders kodu içinde arama yapar",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Kaç kayıt atlanacağı",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Dönecek maksimum kayıt sayısı",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Course)

    if department_id is not None:
        query = query.filter(Course.department_id == department_id)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Course.name.ilike(search_pattern),
                Course.code.ilike(search_pattern),
            )
        )

    total = query.count()

    courses = (
        query
        .order_by(Course.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return CourseListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=courses,
    )


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


@router.post("/recommendations", response_model=CourseRecommendationResponse)
def recommend_courses(
    recommendation_data: CourseRecommendationRequest,
    db: Session = Depends(get_db),
):
    source_course = (
        db.query(Course)
        .filter(Course.id == recommendation_data.source_course_id)
        .first()
    )

    if not source_course:
        raise HTTPException(
            status_code=404,
            detail="Kaynak ders bulunamadı.",
        )

    target_department = (
        db.query(Department)
        .filter(Department.id == recommendation_data.target_department_id)
        .first()
    )

    if not target_department:
        raise HTTPException(
            status_code=404,
            detail="Hedef bölüm bulunamadı.",
        )

    target_courses = (
        db.query(Course)
        .filter(
            Course.department_id == recommendation_data.target_department_id,
            Course.id != recommendation_data.source_course_id,
        )
        .all()
    )

    recommendations = [
        calculate_course_similarity(source_course, target_course)
        for target_course in target_courses
    ]

    recommendations = sorted(
        recommendations,
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    limited_recommendations = recommendations[: recommendation_data.limit]

    return CourseRecommendationResponse(
        source_course_id=source_course.id,
        source_course_name=source_course.name,
        target_department_id=recommendation_data.target_department_id,
        total_candidates=len(recommendations),
        limit=recommendation_data.limit,
        items=limited_recommendations,
    )


@router.get("/comparisons", response_model=CourseComparisonHistoryResponse)
def list_course_comparisons(
    skip: int = Query(
        0,
        ge=0,
        description="Kaç kayıt atlanacağı",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Dönecek maksimum kayıt sayısı",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(CourseComparison)

    total = query.count()

    comparisons = (
        query
        .order_by(CourseComparison.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = [
        build_comparison_history_item(comparison)
        for comparison in comparisons
    ]

    return CourseComparisonHistoryResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.delete(
    "/comparisons/{comparison_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
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


@router.get(
    "/{course_id}/comparisons",
    response_model=CourseComparisonHistoryResponse,
)
def list_comparisons_for_course(
    course_id: int,
    skip: int = Query(
        0,
        ge=0,
        description="Kaç kayıt atlanacağı",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Dönecek maksimum kayıt sayısı",
    ),
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

    query = (
        db.query(CourseComparison)
        .filter(
            or_(
                CourseComparison.source_course_id == course_id,
                CourseComparison.target_course_id == course_id,
            )
        )
    )

    total = query.count()

    comparisons = (
        query
        .order_by(CourseComparison.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = [
        build_comparison_history_item(comparison)
        for comparison in comparisons
    ]

    return CourseComparisonHistoryResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


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