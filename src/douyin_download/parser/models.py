from datetime import date as Date
from dataclasses import dataclass


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
