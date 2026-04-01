from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    # App
    FRONTEND_URL: str = "http://localhost:5173"
    API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
