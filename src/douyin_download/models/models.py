from dataclasses import dataclass
from pathlib import Path

__all__ = ["AccountInfo", "DownloadInfo"]


@dataclass(slots=True)
class AccountInfo:
    id: str
    name: str
    mark: str


@dataclass(slots=True)
class DownloadInfo:
    url: str
    path: Path
    width: int
    height: int
    data_size: int
