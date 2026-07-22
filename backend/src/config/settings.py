"""App configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Polis API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/polis"

    # SQLite override (used when DATABASE_URL starts with sqlite+aiosqlite://)
    sqlite_path: str = "polis.db"
    use_sqlite: bool = False

    # JWT
    jwt_secret_key: str = "CHANGE-ME-SECRET-KEY"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Bcrypt
    bcrypt_rounds: int = 12

    # CORS
    cors_origins: list[str] = ["*"]

    model_config = {"env_prefix": "POLIS_", "env_file": ".env"}

    def model_post_init(self, __context):
        """Auto-detect SQLite mode from database_url."""
        if self.database_url.startswith("sqlite+aiosqlite://"):
            object.__setattr__(self, "use_sqlite", True)


settings = Settings()
