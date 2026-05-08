from pydantic import BaseModel


class DepartmentBase(BaseModel):
    university_id: int
    name: str
    faculty: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True