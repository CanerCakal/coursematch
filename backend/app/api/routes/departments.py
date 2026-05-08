from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.department import Department
from app.models.university import University
from app.schemas.department import DepartmentCreate, DepartmentRead

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentRead)
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


@router.get("/", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.name).all()