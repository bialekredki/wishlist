import logging

from pydantic import BaseModel, BaseSettings, Field, validator


class JWTSettings(BaseModel):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    expiration_minutes: int = 120


class Settings(BaseSettings):
    debug: bool = Field(default=False, description="Debug flag.")
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    log_level: int | str = Field(default=logging.INFO)
    drafts_max_ammount: int = Field(default=10)
    ALLOW_CORS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    @validator("log_level")
    @classmethod
    def __validate_log_level(cls, value: str | int):
        if isinstance(value, int):
            return value
        else:
            level = logging.getLevelName(value)
            if not isinstance(level, str) or level.startswith("Level"):
                raise ValueError("Couldn't find log level %s", value)
            return level


settings = Settings()
