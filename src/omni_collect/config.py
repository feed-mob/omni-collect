from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "OmniCollect"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'omni_collect.db'}"

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_sqlite_database_url(cls, value: str) -> str:
        url = make_url(value)
        database = url.database

        if (
            not url.drivername.startswith("sqlite")
            or database in (None, "", ":memory:")
            or Path(database).is_absolute()
        ):
            return value

        resolved = (PROJECT_ROOT / database).resolve()
        return url.set(database=str(resolved)).render_as_string(hide_password=False)


settings = Settings()
