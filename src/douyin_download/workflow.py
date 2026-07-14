import subprocess
import time
import random
from rich import print
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.filters import is_done
from prompt_toolkit.styles import Style
from typing import Any
import asyncio
from collections.abc import Callable

from douyin_download.config.constant import Colors, PROJECT_ROOT
from douyin_download.config.settings import load_settings, Account, Settings
from douyin_download.config.cookies import input_save_cookies, CookiesManager
from douyin_download.models import DownloadInfo
from douyin_download.requester import (
    RequestItems,
    SessionManager as RequestSessionManager,
)
from douyin_download.parser import Parser
from douyin_download.downloader import (
    DownloadMedia,
    SessionManager as DownloadSessionManager,
)
from douyin_download.cache import dump_cache_data, load_cache_data, delete_cache_file


def run_menu():
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


def xdg_open_config():
    if not (filepath := PROJECT_ROOT / "settings_mine.json").exists():
        filepath = PROJECT_ROOT / "settings_default.json"
    try:
        subprocess.run(["xdg-open", str(filepath)])
        subprocess.run(["xdg-open", str(PROJECT_ROOT / "已下载账号信息.json")])
    except Exception as e:
        print(f"[{Colors.RED}]Error occurred while opening files: {e}")


class DouyinDownload:
    def __init__(
        self,
        accounts: list[Account],
        settings: Settings,
        request_items: RequestItems,
        parser: Parser,
        download_media: DownloadMedia,
        cookies: CookiesManager,
        dump_cache_data: Callable[[Any, str], None] = dump_cache_data,
        delete_cache_file: Callable[[], None] = delete_cache_file,
    ):
        self.accounts = accounts
        self.settings = settings
        self.request_items = request_items
        self.download_media = download_media
        self.cookies = cookies
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

            await self._download(num, account)
            self.delete_cache_file()

            if num % sleep_long_after_deal_account_num == 0:
                print(f"\n[{Colors.CYAN}]已处理 {num} 个账号")
                self._sleep_random(20, 120)
                sleep_long_after_deal_account_num = (
                    self._sleep_long_after_deal_account_num(accounts_num, num)
                )
            elif num != accounts_num:
                self._sleep_random(2, 7)

    @staticmethod
    def _sleep_long_after_deal_account_num(accounts_num: int, is_deal_num: int = 0):
        sleep_long_after_deal_account_num = is_deal_num + random.randint(6, 12)
        if sleep_long_after_deal_account_num < accounts_num:
            print(
                f"\n[{Colors.CYAN}]处理 {sleep_long_after_deal_account_num} 个账号后将休眠较长时间"
            )
        return sleep_long_after_deal_account_num

    @staticmethod
    def _sleep_random(a: float, b: float):
        time_sleep = random.uniform(a, b)
        print(f"\n[{Colors.CYAN}]休眠 {time_sleep} 秒\n")
        time.sleep(time_sleep)

    async def _download(self, num: int, account: Account):
        print(f"[{Colors.CYAN}]\n开始处理第 {num} 个账号" if num else "开始处理账号")
        print(f"[{Colors.CYAN}]账号标识：{account.mark or '空'}")
        print(
            f"[{Colors.CYAN}]最早发布日期：{account.earliest.strftime('%Y-%m-%d')}，"
            f"最晚发布日期：{account.latest.strftime('%Y-%m-%d')}"
        )
        self.cookies.update()
        self.request_items.session.update_cookies()
        self.download_media.session.update_cookies()
        self.dump_cache_data(self.cookies, "cookies")

        items = self.request_items.run(account)
        self.dump_cache_data(items, "items")

        if items:
            download_infos = self.parser.run(account, items)
            self.dump_cache_data(download_infos, "download_infos")

            await self.download_media.run(download_infos)


async def run() -> None:
    accounts, settings = load_settings()

    cookies = CookiesManager()
    request_session = RequestSessionManager(cookies)
    request_items = RequestItems(settings.timeout, cookies, request_session)
    parser = Parser(settings)
    download_session = DownloadSessionManager(settings.timeout, cookies)
    download_media = DownloadMedia(settings.concurrency, download_session)

    downloader = DouyinDownload(
        accounts, settings, request_items, parser, download_media, cookies
    )

    with request_session:
        async with download_session:
            await downloader.run()


async def continue_download_from_cache() -> None:
    account: Account = load_cache_data("account")
    settings: Settings = load_cache_data("settings")
    cookies: CookiesManager = load_cache_data("cookies")
    download_infos: list[DownloadInfo] = load_cache_data("download_infos")
    cookies.update()

    print(f"[{Colors.CYAN}]账号标识：{account.mark or '空'}")
    print(
        f"[{Colors.CYAN}]最早发布日期：{account.earliest.strftime('%Y-%m-%d')}，"
        f"最晚发布日期：{account.latest.strftime('%Y-%m-%d')}"
    )
    async with DownloadSessionManager(settings.timeout, cookies) as download_session:
        downloader = DownloadMedia(settings.concurrency, download_session)
        await downloader.run(download_infos)
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


if __name__ == "__main__":
    main()
