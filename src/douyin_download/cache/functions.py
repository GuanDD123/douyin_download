import shelve
from pathlib import Path
from typing import Any

__all__ = ["dump_cache_data", "load_cache_data", "delete_cache_file"]

cache_file = Path(__file__).resolve().with_name("cache")


def dump_cache_data(data: Any, key: str) -> None:
    with shelve.open(cache_file) as db:
        db[key] = data


def load_cache_data(key: str) -> Any | None:
    with shelve.open(cache_file) as db:
        return db.get(key)


def delete_cache_file() -> None:
    cache_file.unlink(missing_ok=True)
