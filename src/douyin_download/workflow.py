import subprocess
import time
import random
from rich import print
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.filters import is_done
from prompt_toolkit.styles import Style
from typing import Any, Literal
from pathlib import Path
import asyncio
from collections.abc import Callable

from douyin_download.config.constant import Colors, PROJECT_ROOT
from douyin_download.config.models import Account, AccountRoutine, Settings
from douyin_download.config.settings import load_settings
from douyin_download.config.cookies import input_save_cookies, CookiesManager
from douyin_download.requester.request_item_info import (
    RequestItemInfo,
    SessionManager as RequestSessionManager,
)
from douyin_download.parser.models import DownloadInfo
from douyin_download.parser.extract_item_info import (
    extract_account_info,
    extract_item_info_list,
)
from douyin_download.parser.generate_download_info import generate_download_info_list
from douyin_download.downloader.download_media import (
    DownloadMedia,
    SessionManager as DownloadSessionManager,
)
from douyin_download.cache.functions import (
    dump_cache_data,
    load_cache_data,
    delete_cache_file,
)


def run_menu() -> Literal["1", "2", "3", None]:
    style = Style.from_dict(
        {
            "input-selection": "#f5e6e6",
            "number": "#048282 bold",
            "frame.border": "#884444",
            "selected-option": "#df8620 bold",
        }
    )
    result = choice(
        message="Please select and enter:",
        options=[
            ("1", "批量下载账号作品 (配置文件)"),
            ("2", "修改配置文件 (Linux)"),
            ("3", "复制粘贴写入 Cookie"),
            (
                "4",
                "根据缓存信息下载 (下载时非正常退出可用，继续下载当前账号未下载作品)",
            ),
            (None, "Exit"),
        ],
        style=style,
        show_frame=~is_done,
    )
    return result


def xdg_open_config() -> None:
    if not (filepath := PROJECT_ROOT / "settings_mine.json").exists():
        filepath = PROJECT_ROOT / "settings_default.json"
    try:
        subprocess.run(["xdg-open", str(filepath)])
        subprocess.run(["xdg-open", str(PROJECT_ROOT / "已下载账号信息.json")])
    except Exception as e:
        print(f"[{Colors.RED}]Error occurred while opening files: {e}")


def _create_account_save_folder(
    account_info: AccountRoutine, save_folder: Path
) -> Path:
    folder = save_folder / f"UID{account_info.id}_{account_info.mark}_发布作品"
    folder.mkdir(exist_ok=True)
    return folder


def _parse(
    account: Account, item_list: list[dict], settings: Settings
) -> list[DownloadInfo]:
    print(f"[{Colors.CYAN}]\n开始提取账号信息")
    account_info = extract_account_info(
        account.mark, item_list[0], settings.illegal_char
    )
    print(f"[{Colors.CYAN}]账号昵称：{account_info.name}；账号 ID：{account_info.id}")
    item_info_list = extract_item_info_list(item_list, settings, account)
    print(f"[{Colors.CYAN}]当前账号作品数量: {len(item_info_list)}")

    account_save_folder = _create_account_save_folder(
        account_info, settings.save_folder
    )
    download_info_list = generate_download_info_list(
        account_info.mark, item_info_list, account_save_folder, settings
    )

    return download_info_list


class DouyinDownload:
    def __init__(
        self,
        request_item_info: RequestItemInfo,
        download_media: DownloadMedia,
        cookies_manager: CookiesManager,
        parser: Callable[[Account, list[dict], Settings], list[DownloadInfo]] = _parse,
        dump_cache_data: Callable[[Any, str], None] = dump_cache_data,
        delete_cache_file: Callable[[], None] = delete_cache_file,
    ):
        self.accounts, self.settings = load_settings()
        self.request_item_info = request_item_info
        self.download_media = download_media
        self.cookies_manager = cookies_manager
        self.parser = parser
        self.dump_cache_data = dump_cache_data
        self.delete_cache_file = delete_cache_file

    async def run(self) -> None:
        accounts_num = len(self.accounts)
        print(f"[{Colors.CYAN}]共有 {accounts_num} 个账号的作品等待下载")

        sleep_long_after_deal_account_num = self._sleep_long_after_deal_account_num(
            accounts_num
        )
        for num, account in enumerate(self.accounts, start=1):
            self.dump_cache_data(self.settings, "settings")
            self.dump_cache_data(account, "account")

            if num % sleep_long_after_deal_account_num == 0:
                print(f"\n[{Colors.CYAN}]已处理 {num} 个账号")
                self._sleep_random(20, 120)
                sleep_long_after_deal_account_num = (
                    self._sleep_long_after_deal_account_num(accounts_num, num)
                )
            else:
                self._sleep_random(2, 7)

            await self._download(num, account)
            self.delete_cache_file()

    @staticmethod
    def _sleep_long_after_deal_account_num(
        accounts_num: int, is_deal_num: int = 0
    ) -> int:
        sleep_long_after_deal_account_num = is_deal_num + random.randint(6, 12)
        if sleep_long_after_deal_account_num < accounts_num:
            print(
                f"\n[{Colors.CYAN}]处理 {sleep_long_after_deal_account_num} 个账号后将休眠较长时间"
            )
        return sleep_long_after_deal_account_num

    @staticmethod
    def _sleep_random(a: float, b: float) -> None:
        time_sleep = random.uniform(a, b)
        print(f"\n[{Colors.CYAN}]休眠 {time_sleep} 秒\n")
        time.sleep(time_sleep)

    async def _download(self, num: int, account: Account) -> None:
        print(f"[{Colors.CYAN}]\n开始处理第 {num} 个账号" if num else "开始处理账号")
        print(f"[{Colors.CYAN}]账号标识：{account.mark or '空'}")
        print(
            f"[{Colors.CYAN}]最早发布日期：{account.earliest or '空'}，最晚发布日期：{account.latest or '空'}"
        )
        self.cookies_manager.update()
        self.request_item_info.session_manager.update_cookies()
        self.download_media.session_manager.update_cookies()
        self.dump_cache_data(self.cookies_manager, "cookies_manager")

        item_list = self.request_item_info.run(account)
        self.dump_cache_data(item_list, "item_list")

        if item_list:
            download_info_list = self.parser(account, item_list, self.settings)
            self.dump_cache_data(download_info_list, "download_info_list")

            await self.download_media.run(download_info_list)


async def run() -> None:
    _, settings = load_settings()

    cookies_manager = CookiesManager()
    request_session_manager = RequestSessionManager(cookies_manager)
    request_item_info = RequestItemInfo(
        settings.timeout, cookies_manager, request_session_manager
    )
    download_session_manager = DownloadSessionManager(settings.timeout, cookies_manager)
    download_media = DownloadMedia(settings.concurrency, download_session_manager)

    downloader = DouyinDownload(request_item_info, download_media, cookies_manager)

    with request_session_manager:
        async with download_session_manager:
            await downloader.run()


async def continue_download_from_cache() -> None:
    account: Account = load_cache_data("account")
    settings: Settings = load_cache_data("settings")
    cookies_manager: CookiesManager = load_cache_data("cookies_manager")
    download_info_list: list[DownloadInfo] = load_cache_data("download_info_list")
    cookies_manager.update()

    print(f"[{Colors.CYAN}]账号标识：{account.mark or '空'}")
    print(
        f"[{Colors.CYAN}]最早发布日期：{account.earliest or '空'}，最晚发布日期：{account.latest or '空'}"
    )
    async with DownloadSessionManager(
        settings.timeout, cookies_manager
    ) as download_session_manager:
        downloader = DownloadMedia(settings.concurrency, download_session_manager)
        await downloader.run(download_info_list)
    delete_cache_file()


def main() -> None:
    while mode := run_menu():
        if mode == "1":
            asyncio.run(run())
        elif mode == "2":
            xdg_open_config()
            print(f"[{Colors.CYAN}]Press Enter to continue...")
            input()
        elif mode == "3":
            input_save_cookies()
        elif mode == "4":
            asyncio.run(continue_download_from_cache())
    print(f"[{Colors.WHITE}]程序结束运行")
