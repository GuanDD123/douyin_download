import json
from json.decoder import JSONDecodeError
from rich import print
from pathlib import Path
import sys

from .constant import Colors, PROJECT_ROOT, ENCODE
from .models import Account, Settings


def _select_settings_path():
    if (filepath := PROJECT_ROOT / "settings_mine.json").exists():
        return filepath
    return PROJECT_ROOT / "settings_default.json"


def load_settings(
    filepath: Path = _select_settings_path(),
) -> tuple[list[Account], Settings]:
    try:
        with open(filepath, encoding=ENCODE) as f:
            data = json.load(f)
    except JSONDecodeError:
        print(f"[{Colors.RED}]配置文件 settings.json 格式错误，请检查 JSON 格式！")
        sys.exit()

    accounts = [Account(**a) for a in data["accounts"]]
    settings = Settings(**data)

    return accounts, settings
