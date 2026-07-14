from douyin_download.config.settings import Settings
from douyin_download.models import DownloadInfo
from .models import ItemInfo
from .utils import filter_name


class GenerateDownloadInfos:
    def __init__(self, settings: Settings):
        self.settings = settings

    def run(self, mark: str, item_infos: list[ItemInfo]) -> list[DownloadInfo]:
        download_infos = [
            self._generate_download_info(mark, item_info) for item_info in item_infos
        ]
        return download_infos

    def _generate_download_info(self, mark: str, item_info: ItemInfo):
        name_compnent = []
        for key in self.settings.name_format:
            if key == "create_time":
                name_compnent.append(
                    item_info.create_time.strftime(self.settings.date_format)
                )
            else:
                name_compnent.append(getattr(item_info, key))
        name = self.settings.split.join(name_compnent)

        if item_info.type == "video":
            format = ".mp4" if item_info.format == ".dash" else item_info.format
        else:
            format = ".jpeg"
            name = f"{name}_{item_info.index}"
        if self.settings.add_account_mark_to_end_of_name:
            name = f"{name} {self.settings.split} {mark}"
        name = filter_name(name, self.settings.illegal_char)

        path = self.settings.save_folder / f"{name}{format}"
        return DownloadInfo(
            url=item_info.url,
            path=path,
            width=item_info.width,
            height=item_info.height,
            data_size=item_info.data_size,
        )
