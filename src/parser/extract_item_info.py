from datetime import date as Date
from collections.abc import Mapping
from dataclasses import dataclass

from src.parser.cleaner import Cleaner
from src.config.settings import Settings, Account, AccountRoutine


@dataclass(frozen=True, slots=True)
class ItemInfo:
    id: str
    desc: str
    create_timestamp: str
    create_time_date: Date
    create_time: str
    type: str
    share_url: str
    format: str
    url: str
    width: int
    height: int
    index: int


def _extract_value(data: Mapping, attribute_chain: str) -> str | None:
    '''根据 attribute_chain 从 dict 中提取值'''
    attributes = attribute_chain.split('.')
    for attribute in attributes:
        if '[' in attribute:
            parts = attribute.split('[', 1)
            attribute = parts[0]
            index = int(parts[1].split(']', 1)[0])
            data = data[attribute][index]
        else:
            data = data[attribute]
        if not data:
            return None
    return data


def extract_account(account: Account, item: Mapping, cleaner: Cleaner) -> AccountRoutine:
    '''提取账号 id、昵称，规范化账号 mark'''
    id = _extract_value(item, 'author.uid')
    name = cleaner.filter_name(_extract_value(item, 'author.nickname'), default='无效账号昵称')
    mark = cleaner.filter_name(account.mark, default=name)
    return AccountRoutine(id=id, name=name, mark=mark)


class ExtractItems:
    def __init__(self, settings: Settings, cleaner: Cleaner) -> None:
        self.settings = settings
        self.cleaner = cleaner

    def run(self, items: list[Mapping], earliest: Date, latest: Date) -> list[ItemInfo]:
        '''提取发布作品信息并返回'''
        results = []
        for item in items:
            if (_extract_value(item, 'images')):
                if self.settings.download_images:
                    if images := self._extract_images(item, earliest, latest):
                        results.extend(images)
            elif self.settings.download_videos:
                if video := self._extract_video(item, earliest, latest):
                    results.append(video)
        return results

    def _extract_common(self, item: Mapping, earliest: Date, latest: Date) -> dict[str, str] | None:
        '''提取图文/视频作品共有信息'''
        result = {}
        result['id'] = _extract_value(item, 'aweme_id')
        if desc := _extract_value(item, 'desc'):
            result['desc'] = self.cleaner.clear_spaces(self.cleaner.filter_name(desc))[:self.settings.file_description_max_length]
        else:
            result['desc'] = '作品描述为空'
        result['create_timestamp'] = _extract_value(item, 'create_time')
        result['create_time_date'] = Date.fromtimestamp(int(result['create_timestamp']))
        result['create_time'] = Date.strftime(result['create_time_date'], self.settings.date_format)
        if self._is_extra_items(result['create_time_date'], latest, earliest):
            return None
        return result

    def _extract_images(self, images: Mapping, earliest: Date, latest: Date) -> list[ItemInfo] | None:
        '''提取图文作品信息'''
        results = []
        result = self._extract_common(images, earliest, latest)
        if not result:
            return None
        images_info = _extract_value(images, 'images')
        result['type'] = 'image'
        result['share_url'] = f'https://www.douyin.com/note/{result["id"]}'
        for index, image in enumerate(images_info):
            result['index'] = index
            result['url'] = _extract_value(image, 'url_list[0]')
            result['width'] = _extract_value(image, 'width')
            result['height'] = _extract_value(image, 'height')
            results.append(ItemInfo(**result, format=None))
        return results

    def _extract_video(self, video: Mapping, earliest: Date, latest: Date) -> ItemInfo | None:
        '''提取视频作品信息'''
        result = self._extract_common(video, earliest, latest)
        if not result:
            return None
        video_info = _extract_value(video, 'video')
        result['type'] = 'video'
        result['format'] = '.' + _extract_value(video_info, 'format')
        result['share_url'] = f'https://www.douyin.com/video/{result["id"]}'
        result['url'] = _extract_value(video_info, 'play_addr.url_list[0]')
        result['width'] = _extract_value(video_info, 'width')
        result['height'] = _extract_value(video_info, 'height')
        if not self.settings.download_horizontal_video and result['width'] > result['height']:
            return None
        if not self.settings.download_vertical_video and result['width'] < result['height']:
            return None
        return ItemInfo(**result, index=None)

    def _is_extra_items(self, create_time_date: Date, latest: Date, earliest: Date) -> bool:
        if (create_time_date > latest) or (create_time_date < earliest):
            return True
        return False
