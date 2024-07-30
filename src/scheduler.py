from os.path import (
    join as join_path,
    exists,
)
from os import makedirs
from shutil import rmtree
from datetime import date
from rich import print
from time import time

from config import (
    PROJECT_ROOT,
    COOKIE_UPDATE_INTERVAL,
    TEXT_REPLACEMENT,
    YELLOW, WHITE, CYAN
)
from config import Settings, Cookie
from tool import Cleaner
from download import Acquire, Download, Parse
from backup import DownloadRecorder, DownloadItems


class Scheduler:

    def __init__(self) -> None:
        self.download_recorder = DownloadRecorder()
        self.download_items = DownloadItems()
        self.cleaner = Cleaner()
        self.settings = Settings()
        self.cookie = Cookie(self.settings)
        self.parse = Parse(self.cleaner, self.settings)
        self.download = Download(self.settings, self.cleaner, self.cookie, self.download_recorder)
        self.acquirer = Acquire(self.settings)
        self.running = True


    def run(self):
        self.check_config()
        if self.running:
            self.main_menu()
        self.close()

    def check_config(self):
        self.cleaner.set_rule(TEXT_REPLACEMENT)
        cache_folder = join_path(PROJECT_ROOT, 'cache')
        self.running = self.settings.check()
        if exists(cache_folder):
            account, items = self.download_items.read()
            if account and items:
                self.download_recorder.read()
                print(f'[{CYAN}]开始提取上次未下载完作品数据')
                account_id = account['id']
                account_mark = account['mark']
                print(f'[{CYAN}]账号标识：{account_mark}；账号 ID：{account_id}')
                self.download_recorder.open_()
                self.download.download_files(items, account_id, account_mark)
                self.download_recorder.f_obj.close()
        else:
            makedirs(cache_folder)

    def main_menu(self):
        self.cookie.update()
        for i in (
            '可选择的运行模式 (q 退出)',
            f'{'='*25}',
            '1. 复制粘贴写入 Cookie',
            f'{'='*25}',
            '2. 批量下载账号作品(配置文件)',
            f'{'='*25}',
        ):
            print(f'[{CYAN}]{i}')
        while (mode := input('\n请选择运行模式：').strip()).lower() != 'q':
            if mode:
                if mode == '1':
                    self.cookie.input_save()
                elif mode == '2':
                    self.account_acquisition_interactive()

    def account_acquisition_interactive(self):
        accounts = self.settings.accounts
        print(f'[{CYAN}]共有 {len(accounts)} 个账号的作品等待下载')
        for num, account in enumerate(accounts, start=1):
            self.deal_account_works(num, account)
            if time()-self.cookie.last_update_time >= COOKIE_UPDATE_INTERVAL:
                self.cookie.update()

    def deal_account_works(self, num: int, account: dict[str, str | date]):
        print(f'[{CYAN}]\n\n开始处理第 {num} 个账号' if num else '开始处理账号')
        print(f'[{CYAN}]最早发布日期：{account['earliest'] or '空'}，最晚发布日期：{account['latest'] or '空'}')
        items = self.acquirer.request_items(account['sec_user_id'], account['earliest_date'])
        if not any(items):
            print(f'[{YELLOW}]获取账号主页数据失败')
            return False
        else:
            print(f'[{CYAN}]开始提取作品数据')
            self.parse.extract_account(account, items[0])
            account_id = account['id']
            account_mark = account['mark']
            print(f'[{CYAN}]账号标识：{account_mark}；账号 ID：{account_id}')
            items = self.parse.extract_items(items, account['earliest_date'], account['latest_date'])
            self.download_items.save(account, items)
            self.download_recorder.open_()
            self.download.download_files(items, account_id, account_mark)
            self.download_recorder.f_obj.close()
            return True

    def close(self):
        rmtree(join_path(PROJECT_ROOT, 'cache'))
        self.download_recorder.delete()
        self.download_items.delete()
        print(f'[{WHITE}]程序结束运行')
