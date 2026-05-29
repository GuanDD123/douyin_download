import json
from json.decoder import JSONDecodeError
from rich import print
from pathlib import Path
import sys

from douyin_download.config.constant import Colors, PROJECT_ROOT, ENCODE
from douyin_download.config.models import Account, Settings


def load_settings() -> tuple[tuple[Account], Settings]:
    if not (filepath := PROJECT_ROOT / 'settings_mine.json').exists():
        filepath = PROJECT_ROOT / 'settings_default.json'
    try:
        with open(filepath, encoding=ENCODE) as f:
            data = json.load(f)
    except JSONDecodeError:
        print(f'[{Colors.RED}]配置文件 settings.json 格式错误，请检查 JSON 格式！')
        sys.exit()

    accounts = tuple(Account.from_mapping(a) for a in data["accounts"])
    settings = Settings(save_folder=Path(data.get('save_folder') or PROJECT_ROOT),
                        download_videos=data.get('download_videos', True),
                        download_images=data.get('download_images', True),
                        download_horizontal_video=data.get('download_horizontal_video', True),
                        download_vertical_video=data.get('download_vertical_video', True),
                        name_format=tuple(data.get('name_format', ('create_time', 'id', 'type', 'desc'))),
                        split=data.get('split', '-'),
                        date_format=data.get('date_format', '%Y-%m-%d'),
                        add_account_mark_to_end_of_name=data.get('add_account_mark_to_end_of_name', False),
                        file_description_max_length=data.get('file_description_max_length', 64),
                        chunk_size=data.get('chunk_size', 1024 * 1024),
                        timeout=data.get('timeout', 60 * 5),
                        concurrency=data.get('concurrency', 5))
    return accounts, settings


if __name__ == '__main__':
    print(load_settings())
    input()
