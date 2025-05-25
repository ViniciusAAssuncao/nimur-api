from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "NimurAPI"
    DATA_DIRECTORY: str = str(Path.home() / "Hadab")
    INDEX_DIR: str = "nimur_index"
    DEFAULT_SEARCH_LIMIT: int = 10
    MAX_SEARCH_LIMIT: int = 100
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 50
    HIGHLIGHT_MAX_CHARS: int = 250
    HIGHLIGHT_SURROUND: int = 40

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

Path(settings.DATA_DIRECTORY).mkdir(parents=True, exist_ok=True)
Path(settings.INDEX_DIR).mkdir(parents=True, exist_ok=True)