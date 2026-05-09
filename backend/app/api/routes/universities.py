from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.university import University
from app.schemas.university import UniversityCreate, UniversityRead, UniversityUpdate

router = APIRouter(prefix="/universities", tags=["Universities"])


@router.post("/", response_model=UniversityRead, status_code=status.HTTP_201_CREATED)
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


@router.get("/{university_id}", response_model=UniversityRead)
def get_university(
    university_id: int,
    db: Session = Depends(get_db),
):
    university = (
        db.query(University)
        .filter(University.id == university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=404,
            detail="Üniversite bulunamadı.",
        )

    return university


@router.put("/{university_id}", response_model=UniversityRead)
def update_university(
    university_id: int,
    university_data: UniversityUpdate,
    db: Session = Depends(get_db),
):
    university = (
        db.query(University)
        .filter(University.id == university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=404,
            detail="Üniversite bulunamadı.",
        )

    update_data = university_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_university = (
            db.query(University)
            .filter(
                University.name == update_data["name"],
                University.id != university_id,
            )
            .first()
        )

        if existing_university:
            raise HTTPException(
                status_code=400,
                detail="Bu isimde başka bir üniversite zaten var.",
            )

    for field, value in update_data.items():
        setattr(university, field, value)

    db.commit()
    db.refresh(university)

    return university


@router.delete("/{university_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_university(
    university_id: int,
    db: Session = Depends(get_db),
):
    university = (
        db.query(University)
        .filter(University.id == university_id)
        .first()
    )

    if not university:
        raise HTTPException(
            status_code=404,
            detail="Üniversite bulunamadı.",
        )

    db.delete(university)
    db.commit()

    return None