from pathlib import Path
from typing import Set


def ensure_directory_exists(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def is_temp_file(filename: str) -> bool:
    return filename.startswith("~$") or filename.startswith(".")


def get_file_extension(file_path: Path) -> str:
    return file_path.suffix.lower()
