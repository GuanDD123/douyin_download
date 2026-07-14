from rich import print
from pathlib import Path

from douyin_download.config.constant import Colors
from douyin_download.config.settings import Account, Settings
from douyin_download.models import AccountInfo, DownloadInfo
from .extracter import Extracter
from .generate_download_infos import GenerateDownloadInfos

__all__ = ["Parser"]


class Parser:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.extracter = Extracter(settings)
        self.generate_download_infos = GenerateDownloadInfos(settings)

    def run(self, account: Account, items: list[dict]) -> list[DownloadInfo]:
        print(f"[{Colors.CYAN}]\n开始提取账号信息")

        account_info = self.extracter.extract_account_info(account.mark, items[0])
        print(
            f"[{Colors.CYAN}]账号昵称：{account_info.name}；账号 ID：{account_info.id}"
        )
        item_infos = self.extracter.extract_item_infos(items, account)
        print(f"[{Colors.CYAN}]当前账号作品数量: {len(item_infos)}")

        account_save_folder = self._create_account_save_folder(
            account_info, self.settings.save_folder
        )
        download_infos = self.generate_download_infos.run(
            account_info.mark, item_infos, account_save_folder
        )

        return download_infos

    @staticmethod
    def _create_account_save_folder(account_info: AccountInfo, save_folder: Path):
        folder = save_folder / f"UID{account_info.id}_{account_info.mark}_发布作品"
        folder.mkdir(exist_ok=True)
        return folder
