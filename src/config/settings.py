import json
from json.decoder import JSONDecodeError
import re
from datetime import date as Date, datetime as Datetime
import datetime
from rich import print
from dataclasses import dataclass
from pathlib import Path
import os
import sys
from collections.abc import Sequence, Mapping
from collections import namedtuple


PROJECT_ROOT = Path(__file__).parents[2]
ENCODE = 'UTF-8-SIG' if os.name == 'nt' else 'UTF-8'
Colors = namedtuple('Colors', ['WHITE', 'CYAN', 'RED', 'YELLOW', 'GREEN', 'MAGENTA'])
COLORS = Colors('#aaaaaa', 'bright_cyan', 'bright_red', 'bright_yellow', 'bright_green', 'bright_magenta')
REFERER = 'https://www.douyin.com/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
HEADERS = {'Referer': REFERER, 'User-Agent': USER_AGENT}
PHONE_USER_AGENT = 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'
RETRY_ACCOUNT: int = 3
RETRY_FILE: int = 2


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
        print(f'[{COLORS.RED}]参数 accounts 中账号 {mark} 的 url {url} 错误，提取 sec_user_id 失败！')
        sys.exit()

    @staticmethod
    def _generate_date(earliest: str, latest: str) -> tuple[Date, Date]:
        try:
            earliest_date = Datetime.strptime(earliest, '%Y/%m/%d').date()
            latest_date = Datetime.strptime(latest, '%Y/%m/%d').date()
        except ValueError:
            print(f'[{COLORS.YELLOW}]作品发布日期 {earliest}, {latest} 无效，使用默认日期')
            earliest_date = Date(2016, 9, 20)
            latest_date = Date.today() - datetime.timedelta(days=1)
        return earliest_date, latest_date


@dataclass(frozen=True, slots=True)
class Settings:
    accounts: Sequence[Account]
    save_folder: Path
    download_videos: bool
    download_images: bool
    name_format: Sequence[str]
    split: str
    date_format: str
    proxy: str
    file_description_max_length: int
    chunk_size: int
    timeout: int
    concurrency: int


def load_settings() -> Settings:
    if not (filepath := PROJECT_ROOT / 'settings_mine.json').exists():
        filepath = PROJECT_ROOT / 'settings_default.json'
    try:
        with open(filepath, encoding=ENCODE) as f:
            data = json.load(f)
    except JSONDecodeError:
        print(f'[{COLORS.RED}]配置文件 settings.json 格式错误，请检查 JSON 格式！')
        sys.exit()

    accounts = tuple(Account.from_mapping(a) for a in data["accounts"])
    return Settings(accounts=accounts,
                    save_folder=Path(data.get('save_folder', PROJECT_ROOT)),
                    download_videos=data.get('download_videos', True),
                    download_images=data.get('download_images', True),
                    name_format=tuple(data.get('name_format', ('create_time', 'id', 'type', 'desc'))),
                    split=data.get('split', '-'),
                    date_format=data.get('date_format', '%Y-%m-%d'),
                    proxy=data.get('proxy'),
                    file_description_max_length=data.get('file_description_max_length', 64),
                    chunk_size=data.get('chunk_size', 1024 * 1024),
                    timeout=data.get('timeout', 60 * 5),
                    concurrency=data.get('concurrency', 5)
                    )


if __name__ == '__main__':
    print(load_settings())
    input()
