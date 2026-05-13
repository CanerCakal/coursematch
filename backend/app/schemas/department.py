from pydantic import BaseModel


class DepartmentBase(BaseModel):
    university_id: int
    name: str
    faculty: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    university_id: int | None = None
    name: str | None = None
    faculty: str | None = None


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[DepartmentRead]