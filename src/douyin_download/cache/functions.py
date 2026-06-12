import shelve
from pathlib import Path
from typing import Any

cache_filepath = Path(__file__).resolve().with_name("cache")


def dump_cache_data(data: Any, key: str) -> None:
    with shelve.open(cache_filepath) as db:
        db[key] = data


def load_cache_data(key: str) -> Any | None:
    with shelve.open(cache_filepath) as db:
        return db.get(key)


def delete_cache_file() -> None:
    cache_filepath.unlink(missing_ok=True)
