from __future__ import annotations

from typing import TYPE_CHECKING
from rich import print
from collections.abc import Sequence
from pathlib import Path
from dataclasses import dataclass

from src.config.settings import AccountRoutine
from src.config.constant import Colors

if TYPE_CHECKING:
    from src.parser.extract_item_info import ItemInfo
    from src.parser.cleaner import Cleaner


@dataclass(frozen=True, slots=True)
class DownloadInfo:
    url: str
    path: Path
    show: str
    id: str
    width: int
    height: int

def _generate_download_info(account_info: AccountRoutine, add_account_mark_to_end_of_name: bool,
                            item_info: ItemInfo, save_folder: Path,
                            split_tag: str, name_format: str, cleaner: Cleaner) -> DownloadInfo | None:
    show = f'{item_info.type} {item_info.id} {item_info.desc[:15]}'
    name = cleaner.filter_name(split_tag.join(getattr(item_info, key) for key in name_format))
    if item_info.type == 'video':
        format='.mp4' if item_info.format == '.dash' else item_info.format
    else:
        format='.jpeg'
        name = f'{name}_{item_info.index}'
    if add_account_mark_to_end_of_name:
        name = f'{name} {split_tag} {account_info.mark}'
    path = save_folder / f'{name}{format}'
    if path.exists():
        print(f'[{Colors.CYAN}]{show} 文件已存在，跳过下载')
    else:
        return DownloadInfo(url=item_info.url,
                            path=path,
                            show=show,
                            id=item_info.id,
                            width=item_info.width,
                            height=item_info.height)


def generate_download_infos(account_info: AccountRoutine, add_account_mark_to_end_of_name: bool,
                            items_info: Sequence[ItemInfo], save_folder: Path, split_tag: str,
                            name_format: str, cleaner: Cleaner) -> list[DownloadInfo]:
    '''生成视频和图片下载任务信息'''
    download_infos = []
    for item_info in items_info:
        if (download_info := _generate_download_info(account_info, add_account_mark_to_end_of_name,
                                                     item_info, save_folder, split_tag, name_format, cleaner)) is not None:
            download_infos.append(download_info)
    return download_infos
