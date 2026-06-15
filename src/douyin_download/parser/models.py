from datetime import date as Date
from dataclasses import dataclass
from pathlib import Path

__all__ = ["AccountRoutine", "DownloadInfo"]


@dataclass(slots=True)
class AccountRoutine:
    id: str
    name: str
    mark: str


@dataclass(slots=True)
class ItemInfo:
    id: str
    desc: str
    create_timestamp: str
    create_time: Date
    type: str
    share_url: str
    format: str
    url: str
    width: int
    height: int
    index: int
    data_size: int


@dataclass(slots=True)
class DownloadInfo:
    url: str
    path: Path
    width: int
    height: int
    data_size: int
