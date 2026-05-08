import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CourseMatch")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")

    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "coursematch_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "coursematch_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "coursematch_password")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )


settings = Settings()
