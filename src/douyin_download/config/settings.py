import json
from json.decoder import JSONDecodeError
from rich import print
from pathlib import Path
import sys
from platform import system
from string import whitespace

from douyin_download.config.constant import Colors, PROJECT_ROOT, ENCODE
from douyin_download.config.models import Account, Settings


def _generate_default_rule() -> set[str]:
    """根据系统类型生成默认非法字符集合"""
    now_system = system()
    if now_system in ("Windows", "Darwin"):
        rule = {
            "/",
            "\\",
            "|",
            "<",
            ">",
            "'",
            '"',
            "?",
            ":",
            "*",
            "\x00",
        }  # Windows 系统和 Mac 系统
    elif now_system == "Linux":
        rule = {"/", "\x00"}  # Linux 系统
    else:
        print(f"[{Colors.YELLOW}]不受支持的操作系统类型，可能无法正常去除非法字符！")
        rule = set()
    return rule | {i for i in whitespace[1:]}  # 补充换行符等非法字符


def _select_settings_path() -> Path:
    if (filepath := PROJECT_ROOT / "settings_mine.json").exists():
        return filepath
    return PROJECT_ROOT / "settings_default.json"


def load_settings(
    filepath: Path = _select_settings_path(),
) -> tuple[tuple[Account], Settings]:
    try:
        with open(filepath, encoding=ENCODE) as f:
            data = json.load(f)
    except JSONDecodeError:
        print(f"[{Colors.RED}]配置文件 settings.json 格式错误，请检查 JSON 格式！")
        sys.exit()

    accounts = tuple(Account.from_mapping(a) for a in data["accounts"])
    settings = Settings(
        save_folder=Path(data.get("save_folder") or PROJECT_ROOT),
        download_videos=data.get("download_videos", True),
        download_images=data.get("download_images", True),
        download_horizontal_video=data.get("download_horizontal_video", True),
        download_vertical_video=data.get("download_vertical_video", True),
        name_format=tuple(
            data.get("name_format", ("create_time", "id", "type", "desc"))
        ),
        split=data.get("split", "-"),
        date_format=data.get("date_format", "%Y-%m-%d"),
        add_account_mark_to_end_of_name=data.get(
            "add_account_mark_to_end_of_name", False
        ),
        file_description_max_length=data.get("file_description_max_length", 64),
        timeout=data.get("timeout", 60 * 5),
        concurrency=data.get("concurrency", 5),
        illegal_char=_generate_default_rule(),
    )
    return accounts, settings
