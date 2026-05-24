import subprocess
import time
import random
from rich import print
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.filters import is_done
from prompt_toolkit.styles import Style
from typing import Literal
from pathlib import Path
import asyncio
from collections.abc import Sequence, Mapping

from src.config.constant import Colors, PROJECT_ROOT
from src.config.models import Account, AccountRoutine, Settings
from src.config.settings import load_settings
from src.config.cookies import input_save_cookies, load_cookies, Cookies
from src.requester.request_item_info import RequestItems
from src.parser.models import DownloadInfo
from src.parser.cleaner import Cleaner
from src.parser.extract_item_info import extract_account, ExtractItems
from src.parser.generate_download_info import generate_download_infos
from src.downloader.downloader import Downloader
from src.cache.functions import dump_cache_data, load_cache_data, delete_cache_file


def run_menu() -> Literal['1', '2', '3', None]:
    style = Style.from_dict(
        {
            "input-selection": "#f5e6e6",
            "number": "#048282 bold",
            "frame.border": "#884444",
            "selected-option": "#df8620 bold",
        }
    )
    result = choice(
        message='Please select and enter:',
        options=[
            ('1', '批量下载账号作品 (配置文件)'),
            ('2', '修改配置文件 (Linux)'),
            ('3', '复制粘贴写入 Cookie'),
            ('4', '根据缓存信息下载 (下载时非正常退出可用，继续下载当前账号未下载作品)')
            (None, 'Exit')
        ],
        style=style,
        show_frame=~is_done,
    )
    return result


def xdg_open_config() -> None:
    if not (filepath := PROJECT_ROOT / 'settings_mine.json').exists():
        filepath = PROJECT_ROOT / 'settings_default.json'
    try:
        subprocess.run(['xdg-open', str(filepath)])
        subprocess.run(['xdg-open', str(PROJECT_ROOT / '已下载账号信息.json')])
    except Exception as e:
        print(f'[{Colors.RED}]Error occurred while opening files: {e}')


def _create_account_save_folder(account_info: AccountRoutine, save_folder: Path):
    '''新建存储文件夹，返回文件夹路径'''
    folder = save_folder / f'UID{account_info.id}_{account_info.mark}_发布作品'
    folder.mkdir(exist_ok=True)
    return folder


def _parse(account: Account, items: Sequence[Mapping], extract_items: ExtractItems, cleaner: Cleaner,
          settings: Settings) -> list[DownloadInfo]:
    print(f'[{Colors.CYAN}]\n开始提取账号信息')
    account_info = extract_account(account, items[0], cleaner)
    print(f'[{Colors.CYAN}]账号昵称：{account_info.name}；账号 ID：{account_info.id}')
    item_infos = extract_items.run(items, account.earliest_date, account.latest_date)
    print(f'[{Colors.CYAN}]当前账号作品数量: {len(item_infos)}')

    account_save_folder = _create_account_save_folder(account_info, settings.save_folder)
    download_infos = generate_download_infos(account_info, settings.add_account_mark_to_end_of_name,
                                             item_infos, account_save_folder, settings.split, settings.name_format, cleaner)

    return download_infos


async def _download(settings: Settings, cookies: Cookies, download_infos: Sequence[DownloadInfo]):
    async with Downloader(settings=settings, cookies=cookies, download_infos=download_infos) as downloader:
        await downloader.run()


def run() -> None:
    settings = load_settings()
    cookies = load_cookies()
    cleaner = Cleaner()
    extract_items = ExtractItems(settings=settings, cleaner=cleaner)
    dump_cache_data(settings, 'settings')

    accounts = settings.accounts
    print(f'[{Colors.CYAN}]共有 {len(accounts)} 个账号的作品等待下载')

    for num, account in enumerate(accounts, start=1):
        dump_cache_data(account, 'account')

        if num != 1 and num % 5 == 1:
            sleep_time = random.randint(20, 180)
            print(f'[{Colors.CYAN}]已处理 {num - 1} 个账号，等待 {sleep_time} 秒后继续')
            time.sleep(sleep_time)

        print(f'[{Colors.CYAN}]\n开始处理第 {num} 个账号' if num else '开始处理账号')
        print(f'[{Colors.CYAN}]账号标识：{account.mark or "空"}')
        print(f'[{Colors.CYAN}]最早发布日期：{account.earliest or "空"}，最晚发布日期：{account.latest or "空"}')
        cookies.update()
        dump_cache_data(cookies, 'cookies')

        with RequestItems(settings, cookies, account) as requestor:
            items = requestor.run()
        dump_cache_data(items, 'items')

        if items:
            download_infos = _parse(account, items, extract_items, cleaner, settings)
            dump_cache_data(download_infos, 'download_infos')

            asyncio.run(_download(settings, cookies, download_infos))

    delete_cache_file()


def continue_download_from_cache() -> None:
    account = load_cache_data('account')
    settings = load_cache_data('settings')
    cookies = load_cache_data('cookies')
    download_infos = load_cache_data('download_infos')

    print(f'[{Colors.CYAN}]账号标识：{account.mark or "空"}')
    print(f'[{Colors.CYAN}]最早发布日期：{account.earliest or "空"}，最晚发布日期：{account.latest or "空"}')
    asyncio.run(_download(settings, cookies, download_infos))
    delete_cache_file()


def main() -> None:
    while (mode := run_menu()):
        if mode == '1':
            run()
        elif mode == '2':
            xdg_open_config()
            print(f'[{Colors.CYAN}]Press Enter to continue...')
            input()
        elif mode == '3':
            input_save_cookies()
        elif mode == '4':
            continue_download_from_cache()
    print(f'[{Colors.WHITE}]程序结束运行')
