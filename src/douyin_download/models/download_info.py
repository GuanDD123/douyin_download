from dataclasses import dataclass
from pathlib import Path

__all__ = ["DownloadInfo"]


@dataclass(slots=True)
class DownloadInfo:
    url: str
    path: Path
    width: int
    height: int
    data_size: int
