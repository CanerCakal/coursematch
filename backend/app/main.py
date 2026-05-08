from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Üniversiteler arası ders karşılaştırma sistemi API servisi",
    version=settings.APP_VERSION,
)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API çalışıyor",
        "version": settings.APP_VERSION
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
