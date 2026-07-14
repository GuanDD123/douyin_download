from dataclasses import dataclass
from pathlib import Path

__all__ = ["AccountRoutine", "DownloadInfo"]


@dataclass(slots=True)
class AccountRoutine:
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
