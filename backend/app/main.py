from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import courses, departments, universities
from app.core.config import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Üniversiteler arası ders karşılaştırma sistemi API servisi",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API çalışıyor",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


app.include_router(universities.router)
app.include_router(departments.router)
app.include_router(courses.router)