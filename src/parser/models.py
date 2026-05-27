from datetime import date as Date
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ItemInfo:
    id: str
    desc: str
    create_timestamp: str
    create_time_date: Date
    create_time: str
    type: str
    share_url: str
    format: str
    url: str
    width: int
    height: int
    index: int
    data_size: int


@dataclass(frozen=True, slots=True)
class DownloadInfo:
    url: str
    path: Path
    show: str
    id: str
    width: int
    height: int
    data_size: int
