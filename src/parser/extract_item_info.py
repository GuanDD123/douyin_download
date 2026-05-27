from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import date as Date
from collections.abc import Mapping, Sequence

from src.config.models import Settings, Account, AccountRoutine
from src.parser.models import ItemInfo

if TYPE_CHECKING:
    from src.parser.cleaner import Cleaner


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

    def run(self, items: Sequence[Mapping], earliest: Date, latest: Date) -> list[ItemInfo]:
        '''提取发布作品信息并返回'''
        items_info = []
        for item in items:
            result = self._extract_common(item)
            if (result['create_time_date'] > latest) or (result['create_time_date'] < earliest):
                continue
            if (images := _extract_value(item, 'images')):
                if self.settings.download_images:
                    if images_info := self._extract_images(images, result):
                        items_info.extend(images_info)
            elif (video := _extract_value(item, 'video')):
                if self.settings.download_videos:
                    if video_info := self._extract_video(video, result):
                        items_info.append(video_info)
        return items_info

    def _extract_common(self, item: Mapping) -> dict[str, str]:
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
        return result

    def _extract_images(self, images: Mapping, result: Mapping) -> list[ItemInfo]:
        '''提取图文作品信息'''
        results = []
        result['type'] = 'image'
        result['share_url'] = f'https://www.douyin.com/note/{result["id"]}'
        for index, image in enumerate(images):
            result['index'] = index
            result['url'] = _extract_value(image, 'url_list[0]')
            result['width'] = _extract_value(image, 'width')
            result['height'] = _extract_value(image, 'height')
            results.append(ItemInfo(**result, format=None, data_size=None))
        return results

    def _extract_video(self, video: Mapping, result: Mapping) -> ItemInfo | None:
        '''提取视频作品信息'''
        result['type'] = 'video'
        result['format'] = '.' + _extract_value(video, 'format')
        result['share_url'] = f'https://www.douyin.com/video/{result["id"]}'
        result['url'] = _extract_value(video, 'play_addr.url_list[0]')
        result['width'] = _extract_value(video, 'play_addr.width')
        result['height'] = _extract_value(video, 'play_addr.height')
        result['data_size'] = _extract_value(video, 'play_addr.data_size')
        if not self.settings.download_horizontal_video and result['width'] > result['height']:
            return None
        if not self.settings.download_vertical_video and result['width'] < result['height']:
            return None
        return ItemInfo(**result, index=None)
