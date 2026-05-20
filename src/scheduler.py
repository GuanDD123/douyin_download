from rich import print
from rich.prompt import Prompt
from textwrap import dedent
import subprocess
from time import sleep
from random import randint

from src.config import Account, load_settings, Cookie, Colors, PROJECT_ROOT
from src.tool import Cleaner
from src.download import Acquire, Download, Parse


class Scheduler:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.cookie = Cookie()
        self.cleaner = Cleaner()

    def _deal_account(self, num: int, account: Account):
        for i in (
            f'\n开始处理第 {num} 个账号' if num else '开始处理账号',
            f'账号标识：{account.mark or "空"}',
            f'最早发布日期：{account.earliest or "空"}，最晚发布日期：{account.latest or "空"}'
        ):
            print(f'[{Colors.CYAN}]{i}')
        items = Acquire().request_items(account.sec_user_id, account.earliest_date, self.settings, self.cookie)
        if items:
            print(f'[{Colors.CYAN}]\n开始提取作品数据')
            Parse.extract_account(account, items[0], self.cleaner)
            print(f'[{Colors.CYAN}]账号昵称：{account.name}；账号 ID：{account.id}')
            items = Parse.extract_items(items, account.earliest_date, account.latest_date,
                                        self.settings, self.cleaner)
            print(f'[{Colors.CYAN}]当前账号作品数量: {len(items)}')
            Download.download_files(items, account.id, account.mark,
                                    self.settings, self.cleaner, self.cookie)
            return True

    def _deal_accounts(self):
        accounts = self.settings.accounts
        print(f'[{Colors.CYAN}]共有 {len(accounts)} 个账号的作品等待下载')
        for num, account in enumerate(accounts, start=1):
            if num % 5 == 0:
                sleep_time = randint(20, 180)
                print(f'[{Colors.CYAN}]已处理 {num-1} 个账号，等待 {sleep_time} 秒后继续')
                sleep(sleep_time)
            self.cookie.update()
            self._deal_account(num, account)

    def run(self):
        tips = dedent(
            f'''
            {'='*25}
            1. 复制粘贴写入 Cookie
            2. 修改配置文件(Linux)
            {'='*25}
            3. 批量下载账号作品(配置文件)
            {'='*25}

            请选择运行模式：''')
        while (mode := Prompt.ask(f'[{Colors.CYAN}]{tips}', choices=['q', '1', '2', '3'], default='3')) != 'q':
            if mode == '1':
                self.cookie.input_save()
            elif mode == '2':
                if not (filepath := PROJECT_ROOT / 'settings_mine.json').exists():
                    filepath = PROJECT_ROOT / 'settings_default.json'
                subprocess.run(['xdg-open', str(filepath)])
                try:
                    subprocess.run(['xdg-open', str(PROJECT_ROOT / '已下载账号信息.json')])
                except:
                    pass
                input()
                self.settings = load_settings()
            elif mode == '3':
                self.cookie.load_cookies()
                self._deal_accounts()
        print(f'[{Colors.WHITE}]程序结束运行')




from rich.prompt import Prompt
from rich import print
import asyncio
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.filters import is_done
from prompt_toolkit.styles import Style
from typing import Literal

from src.config.settings import COLORS
from src.config.cookies import Cookies


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
            ('1', '复制粘贴写入 Cookie'),
            ('2', '修改配置文件(Linux)'),
            ('3', '批量下载账号作品(配置文件)'),
            (None, 'Exit')
        ],
        style=style,
        show_frame=~is_done,
    )
    return result

def _xdg_open_config() -> None:
    if not (filepath := PROJECT_ROOT / 'settings_mine.json').exists():
        filepath = PROJECT_ROOT / 'settings_default.json'
    try:
        subprocess.run(['xdg-open', str(filepath)])
        subprocess.run(['xdg-open', str(PROJECT_ROOT / '已下载账号信息.json')])
    except Exception as e:
        print(f'[{COLORS.RED}]Error occurred while opening files: {e}')

def main() -> None:
    while (mode := run_menu()):
        cookies = Cookies()
        cleaner = Cleaner()
        if mode == '1':
            cookies.input_save()
        elif mode == '2':
            _xdg_open_config()
        elif mode == '3':
            settings = load_settings()
            cookies.load_cookies()
            _deal_accounts()
    print(f'[{Colors.WHITE}]程序结束运行')
