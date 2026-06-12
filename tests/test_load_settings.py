from pathlib import Path, PosixPath
import datetime

from douyin_download.config.settings import load_settings
from douyin_download.config.models import Account, Settings


def test_load_settings():
    result = (
        (
            Account(
                mark="fake_mark /fwa*?81",
                url="https://www.douyin.com/user/fake_mark /fwa*?81",
                earliest="",
                latest="",
                sec_user_id="fake_mark",
                earliest_date=datetime.date(2016, 9, 20),
                latest_date=datetime.date(2026, 5, 30),
            ),
        ),
        Settings(
            save_folder=PosixPath("/tmp"),
            download_videos=True,
            download_images=True,
            download_horizontal_video=True,
            download_vertical_video=True,
            name_format=("create_time", "id", "type", "desc"),
            split="-",
            date_format="%Y-%m-%d",
            add_account_mark_to_end_of_name=False,
            file_description_max_length=64,
            timeout=300,
            concurrency=5,
            illegal_char={"\r", "/", "\t", "\x0b", "\x0c", "\x00", "\n"},
        ),
    )
    assert load_settings(Path("tests/data/settings_default.json")) == result
