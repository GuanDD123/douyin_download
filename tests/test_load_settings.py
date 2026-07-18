from pathlib import Path
import datetime

from douyin_download.config.settings import load_settings


def test_load_settings():
    accounts, settings = load_settings(Path("tests/data/settings_default.json"))

    assert accounts[0].mark == "fake_mark /fwa*?81"
    assert accounts[0].url == "https://www.douyin.com/user/fake_mark"
    assert accounts[0].earliest == datetime.date(2016, 9, 20)
    assert accounts[0].latest == datetime.date(2026, 7, 17)
    assert accounts[0].sec_user_id == "fake_mark"
    assert settings.save_folder == Path("/tmp")
    assert settings.download_videos is True
    assert settings.download_images is True
    assert settings.download_horizontal_video is True
    assert settings.download_vertical_video is True
    assert settings.name_format == ["create_time", "id", "type", "desc"]
    assert settings.split == "-"
    assert settings.date_format == "%Y-%m-%d"
    assert settings.add_account_mark_to_end_of_name is False
    assert settings.file_description_max_length == 64
    assert settings.timeout == 300
    assert settings.concurrency == 5
    assert settings.illegal_char == {
        "\r",
        "/",
        "\t",
        "\x0b",
        "\x0c",
        "\x00",
        "\n",
        "@",
        "#",
    }
