import json
from json.decoder import JSONDecodeError
from rich import print
from pathlib import Path
import sys
import re
from datetime import date as Date, datetime as Datetime
import datetime
from platform import system
from string import whitespace
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from pydantic_core import PydanticUseDefault

from .constant import Colors, PROJECT_ROOT, ENCODE, URL_PATTERN


class Account(BaseModel):
    mark: str
    url: str
    earliest: Date = Date(2016, 9, 20)
    latest: Date = Date.today() - datetime.timedelta(days=1)

    @field_validator("earliest", "latest", mode="before")
    @classmethod
    def _parse_date(cls, value):
        if value in (None, ""):
            raise PydanticUseDefault()

        for format in ("%Y-%m-%d", "%Y/%m/%d"):
            try:
                return Datetime.strptime(value, format).date()
            except ValueError:
                pass
        raise ValueError(f"invalid date format: {value}")

    @field_validator("url", mode="after")
    @classmethod
    def _match_pattern(cls, value):
        match = re.fullmatch(URL_PATTERN, value)
        if not match:
            raise ValueError("invalid douyin url")
        return match.group(1)

    @model_validator(mode="after")
    def _validate_dates(self):
        if self.earliest > self.latest:
            raise ValueError("earliest date cannot be later than latest date")
        return self

    @computed_field
    @property
    def sec_user_id(self) -> str:
        return self.url.removeprefix("https://www.douyin.com/user/")


class Settings(BaseModel):
    save_folder: Path = PROJECT_ROOT
    download_videos: bool = True
    download_images: bool = True
    download_horizontal_video: bool = True
    download_vertical_video: bool = True
    name_format: list[str] = ["create_time", "id", "type", "desc"]
    split: str = "-"
    date_format: str = "%Y-%m-%d"
    add_account_mark_to_end_of_name: bool = False
    file_description_max_length: int = 64
    timeout: int = 60 * 5
    concurrency: int = 5
    illegal_char: set[str] = Field(default_factory=set)

    model_config = {"extra": "ignore"}

    @field_validator("*", mode="before")
    @classmethod
    def _use_default(cls, value):
        if value in (None, "", []):
            raise PydanticUseDefault()
        if value == 0 and not isinstance(value, bool):
            raise PydanticUseDefault()
        return value

    def model_post_init(self, __context=None):
        self.illegal_char = (
            self._generate_default_illegal_char()
            | {i for i in whitespace[1:]}
            | self.illegal_char
        )

    @staticmethod
    def _generate_default_illegal_char():
        """根据系统类型生成默认非法字符集合"""
        if (now_system := system()) in ("Windows", "Darwin"):
            return {
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
            return {"/", "\x00"}  # Linux 系统
        else:
            print(
                f"[{Colors.YELLOW}]不受支持的操作系统类型，可能无法正常去除非法字符！"
            )
            return set()


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
