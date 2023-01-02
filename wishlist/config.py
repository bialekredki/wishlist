from pydantic import BaseModel, BaseSettings, Field


class JWTSettings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    expiration_minutes: int = 120


class Settings(BaseSettings):
    debug: bool = Field(default=False, description="Debug flag.")
    jwt: JWTSettings = Field(default_factory=JWTSettings)


settings = Settings()
