from __future__ import annotations

from typing import TYPE_CHECKING
from collections.abc import Sequence
from pathlib import Path

from douyin_download.config.models import Settings
from douyin_download.parser.models import ItemInfo, DownloadInfo

if TYPE_CHECKING:
    from douyin_download.parser.cleaner import Cleaner


def _generate_download_info(mark: str, item_info: ItemInfo,
                            save_folder: Path, settings: Settings, cleaner: Cleaner) -> DownloadInfo | None:
    name = cleaner.filter_name(settings.split.join(getattr(item_info, key) for key in settings.name_format))
    if item_info.type == 'video':
        format = '.mp4' if item_info.format == '.dash' else item_info.format
    else:
        format = '.jpeg'
        name = f'{name}_{item_info.index}'
    if settings.add_account_mark_to_end_of_name:
        name = f'{name} {settings.split} {mark}'
    path = save_folder / f'{name}{format}'
    return DownloadInfo(url=item_info.url,
                        path=path,
                        width=item_info.width,
                        height=item_info.height,
                        data_size=item_info.data_size)


def generate_download_infos(mark: str, item_infos: Sequence[ItemInfo],
                            save_folder: Path, settings: Settings, cleaner: Cleaner) -> list[DownloadInfo]:
    '''生成视频和图片下载任务信息'''
    download_infos = []
    for item_info in item_infos:
        if (download_info := _generate_download_info(mark, item_info, save_folder,
                                                     settings, cleaner)) is not None:
            download_infos.append(download_info)
    return download_infos
