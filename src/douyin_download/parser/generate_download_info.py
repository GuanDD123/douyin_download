from pathlib import Path

from douyin_download.config.models import Settings
from douyin_download.parser.models import ItemInfo, DownloadInfo
from douyin_download.parser.tool import filter_name


def _generate_download_info(
    mark: str, item_info: ItemInfo, save_folder: Path, settings: Settings
) -> DownloadInfo:
    name = settings.split.join(getattr(item_info, key) for key in settings.name_format)
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


def generate_download_info_list(
    mark: str, item_info_list: list[ItemInfo], save_folder: Path, settings: Settings
) -> list[DownloadInfo]:
    download_info_list = [
        _generate_download_info(mark, item_info, save_folder, settings)
        for item_info in item_info_list
    ]
    return download_info_list
