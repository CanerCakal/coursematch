from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.university import University
from app.schemas.university import UniversityCreate, UniversityRead

router = APIRouter(prefix="/universities", tags=["Universities"])


@router.post("/", response_model=UniversityRead)
def create_university(
    university_data: UniversityCreate,
    db: Session = Depends(get_db),
):
    existing_university = (
        db.query(University)
        .filter(University.name == university_data.name)
        .first()
    )

    if existing_university:
        raise HTTPException(
            status_code=400,
            detail="Bu isimde bir üniversite zaten var.",
        )

    university = University(**university_data.model_dump())

    db.add(university)
    db.commit()
    db.refresh(university)

    return university


@router.get("/", response_model=list[UniversityRead])
def list_universities(db: Session = Depends(get_db)):
    return db.query(University).order_by(University.name).all()