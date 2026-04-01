from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    APP_NAME: str = "OmniCollect"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'omni_collect.db'}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
