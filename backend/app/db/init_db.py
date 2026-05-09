from app.db.base import Base
from app.db.database import engine

# Model importları gerekli.
# Bu importlar olmadan SQLAlchemy tablo sınıflarını tanımaz.
from app.models import Course, Department, University  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)