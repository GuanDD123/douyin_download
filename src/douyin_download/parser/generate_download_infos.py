from pathlib import Path

from douyin_download.config.settings import Settings
from douyin_download.models import DownloadInfo
from .models import ItemInfo
from .utils import filter_name

__all__ = ["generate_download_infos"]


def _generate_download_info(
    mark: str, item_info: ItemInfo, save_folder: Path, settings: Settings
):
    name_compnent = []
    for key in settings.name_format:
        if key == "create_time":
            name_compnent.append(item_info.create_time.strftime(settings.date_format))
        else:
            name_compnent.append(getattr(item_info, key))
    name = settings.split.join(name_compnent)

    if item_info.type == "video":
        format = ".mp4" if item_info.format == ".dash" else item_info.format
    else:
        format = ".jpeg"
        name = f"{name}_{item_info.index}"
    if settings.add_account_mark_to_end_of_name:
        name = f"{name} {settings.split} {mark}"
    name = filter_name(name, settings.illegal_char)

    path = save_folder / f"{name}{format}"
    return DownloadInfo(
        url=item_info.url,
        path=path,
        width=item_info.width,
        height=item_info.height,
        data_size=item_info.data_size,
    )


def generate_download_infos(
    mark: str, item_infos: list[ItemInfo], save_folder: Path, settings: Settings
) -> list[DownloadInfo]:
    download_infos = [
        _generate_download_info(mark, item_info, save_folder, settings)
        for item_info in item_infos
    ]
    return download_infos
