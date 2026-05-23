import shelve
from pathlib import Path
from typing import Any

backup_filepath = Path(__file__).resolve().with_name('backup')


def backup_data(data: Any, key: str) -> None:
    with shelve.open(backup_filepath) as db:
        db[key] = data


def load_backup_data(key: str) -> Any | None:
    with shelve.open(backup_filepath) as db:
        return db.get(key)


def delete_backup_file() -> None:
    backup_filepath.unlink(missing_ok=True)
