from pydantic import BaseModel


class UniversityBase(BaseModel):
    name: str
    city: str | None = None
    country: str | None = None
    website: str | None = None


class UniversityCreate(UniversityBase):
    pass


class UniversityUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    country: str | None = None
    website: str | None = None


class UniversityRead(UniversityBase):
    id: int

    class Config:
        from_attributes = True