from rich import print
from pathlib import Path

from douyin_download.config.constant import Colors
from douyin_download.config.settings import Account, Settings
from douyin_download.models import AccountRoutine, DownloadInfo
from .extract_item_infos import extract_account_info, extract_item_infos
from .generate_download_infos import generate_download_infos

__all__ = ["parse_to_download_infos"]


def _create_account_save_folder(
    account_info: AccountRoutine, save_folder: Path
) -> Path:
    folder = save_folder / f"UID{account_info.id}_{account_info.mark}_发布作品"
    folder.mkdir(exist_ok=True)
    return folder


def parse_to_download_infos(
    account: Account, items: list[dict], settings: Settings
) -> list[DownloadInfo]:
    print(f"[{Colors.CYAN}]\n开始提取账号信息")
    account_info = extract_account_info(
        account.mark, items[0], settings.illegal_char
    )
    print(f"[{Colors.CYAN}]账号昵称：{account_info.name}；账号 ID：{account_info.id}")
    item_infos = extract_item_infos(items, settings, account)
    print(f"[{Colors.CYAN}]当前账号作品数量: {len(item_infos)}")

    account_save_folder = _create_account_save_folder(
        account_info, settings.save_folder
    )
    download_infos = generate_download_infos(
        account_info.mark, item_infos, account_save_folder, settings
    )

    return download_infos
