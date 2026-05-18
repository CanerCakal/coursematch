from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.department import Department
from app.models.university import University
from app.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentRead,
    DepartmentUpdate,
)

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
):
    university = (
        db.query(University)
        .filter(University.id == department_data.university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=404,
            detail="Üniversite bulunamadı.",
        )

    department = Department(**department_data.model_dump())

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.get("/", response_model=DepartmentListResponse)
def list_departments(
    university_id: int | None = Query(
        None,
        description="Belirli bir üniversiteye ait bölümleri filtreler",
    ),
    search: str | None = Query(
        None,
        description="Bölüm adı veya fakülte adı içinde arama yapar",
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
    query = db.query(Department)

    if university_id is not None:
        query = query.filter(Department.university_id == university_id)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Department.name.ilike(search_pattern),
                Department.faculty.ilike(search_pattern),
            )
        )

    total = query.count()

    departments = (
        query
        .order_by(Department.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return DepartmentListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=departments,
    )


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Bölüm bulunamadı.",
        )

    return department


@router.put("/{department_id}", response_model=DepartmentRead)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Bölüm bulunamadı.",
        )

    update_data = department_data.model_dump(exclude_unset=True)

    if "university_id" in update_data:
        university = (
            db.query(University)
            .filter(University.id == update_data["university_id"])
            .first()
        )

        if not university:
            raise HTTPException(
                status_code=404,
                detail="Üniversite bulunamadı.",
            )

    for field, value in update_data.items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)

    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Bölüm bulunamadı.",
        )

    db.delete(department)
    db.commit()

    return None