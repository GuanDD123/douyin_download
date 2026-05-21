from __future__ import annotations

from typing import TYPE_CHECKING
from rich import print
from collections.abc import Sequence
from pathlib import Path
from dataclasses import dataclass

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

def _generate_download_info(item_info: ItemInfo, save_folder: Path, split_tag: str, name_format: str,
                             cleaner: Cleaner) -> DownloadInfo | None:
    name = cleaner.filter_name(split_tag.join(getattr(item_info, key) for key in name_format))
    show = f'{item_info.type} {item_info.id} {item_info.desc[:15]}'
    if item_info.type == 'video':
        format='.mp4' if item_info.format == '.dash' else item_info.format
        path = save_folder / f'{name}{format}'
    else:
        format='.jpeg'
        path = save_folder / f'{name}_{item_info.index}{format}'
    if path.exists():
        print(f'[{Colors.CYAN}]{show} 文件已存在，跳过下载')
    else:
        return DownloadInfo(url=item_info.url,
                            path=path,
                            show=show,
                            id=item_info.id,
                            width=item_info.width,
                            height=item_info.height)


def generate_download_infos(items_info: Sequence[ItemInfo], save_folder: Path, split_tag: str, name_format: str,
                             cleaner: Cleaner) -> list[DownloadInfo]:
    '''生成视频和图片下载任务信息'''
    download_infos = []
    for item_info in items_info:
        if (download_info := _generate_download_info(item_info, save_folder, split_tag, name_format, cleaner)) is not None:
            download_infos.append(download_info)
    return download_infos
