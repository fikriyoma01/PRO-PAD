from pydantic import BaseModel
import os

class Settings(BaseModel):
    APP_NAME: str = "PRO-PAD API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://propad:propad@localhost:5432/propad")
    JWT_OIDC_ISSUER: str = os.getenv("JWT_OIDC_ISSUER", "https://sso.example/realms/propad")
    JWT_OIDC_AUDIENCE: str = os.getenv("JWT_OIDC_AUDIENCE", "propad-api")
    ENABLE_METRICS: bool = True

settings = Settings()
