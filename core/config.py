from pydantic import BaseSettings
from pydantic import validator


class _Settings(BaseSettings):
    pg_host: str
    pg_port: int
    pg_db: str
    pg_user: str
    pg_password: str
    db_url: str = None

    class Config:
        env_file = "../.env"

    @validator("db_url", pre=True, always=True)
    def construct_db_url(cls, value, values):
        return (
            f"postgresql+asyncpg://"
            f"{values['pg_user']}:{values['pg_password']}"
            f"@{values['pg_host']}:{values['pg_port']}/{values['pg_db']}"
        )


settings = _Settings()
