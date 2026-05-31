from dataclasses import dataclass
import re
from datetime import date as Date, datetime as Datetime
import datetime
from rich import print
from pathlib import Path
import sys
from collections.abc import Sequence, Mapping, Set

from douyin_download.config.constant import Colors


@dataclass(frozen=True, slots=True)
class AccountRoutine:
    id: str
    name: str
    mark: str

@dataclass(frozen=True, slots=True)
class Account:
    mark: str
    url: str
    earliest: str
    latest: str
    sec_user_id: str
    earliest_date: Date
    latest_date: Date

    @classmethod
    def from_mapping(cls, data: Mapping[str, str]) -> 'Account':
        mark = data['mark']
        url = data['url']
        earliest = data['earliest']
        latest = data['latest']
        sec_user_id = cls._extract_sec_user_id(mark, url)
        earliest_date, latest_date = cls._generate_date(earliest, latest)
        return cls(mark=mark,
                   url=url,
                   earliest=earliest,
                   latest=latest,
                   sec_user_id=sec_user_id,
                   earliest_date=earliest_date,
                   latest_date=latest_date)

    @staticmethod
    def _extract_sec_user_id(mark: str, url: str) -> str | None:
        match_url = re.match(r'https://www\.douyin\.com/user/([A-Za-z0-9_-]+)(\?.*)?', url)
        if match_url:
            return match_url.group(1)
        print(f'[{Colors.RED}]参数 accounts 中账号 {mark} 的 url {url} 错误，提取 sec_user_id 失败！')
        sys.exit()

    @staticmethod
    def _generate_date(earliest: str, latest: str) -> tuple[Date, Date]:
        try:
            earliest_date = Datetime.strptime(earliest, '%Y/%m/%d').date()
        except ValueError:
            if earliest:
                print(f'[{Colors.YELLOW}]作品发布日期 {earliest} 无效，使用默认日期')
            earliest_date = Date(2016, 9, 20)
        try:
            latest_date = Datetime.strptime(latest, '%Y/%m/%d').date()
        except ValueError:
            if latest:
                print(f'[{Colors.YELLOW}]作品发布日期 {latest} 无效，使用默认日期')
            latest_date = Date.today() - datetime.timedelta(days=1)
        return earliest_date, latest_date


@dataclass(frozen=True, slots=True)
class Settings:
    save_folder: Path
    download_videos: bool
    download_images: bool
    download_horizontal_video: bool
    download_vertical_video: bool
    name_format: Sequence[str]
    split: str
    date_format: str
    add_account_mark_to_end_of_name: bool
    file_description_max_length: int
    timeout: int
    concurrency: int
    illegal_char: Set
