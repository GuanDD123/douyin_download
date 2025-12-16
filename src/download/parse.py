from datetime import date

from ..tool import Cleaner
from ..config import Settings, Account


class Parse:
    @staticmethod
    def _extract_value(data: dict, attribute_chain: str):
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
                return
        return data

    @staticmethod
    def extract_account(account: Account, item: dict, cleaner: Cleaner):
        '''提取账号 id、昵称，检查账号 mark'''
        account.id = Parse._extract_value(item, 'author.uid')
        account.name = cleaner.filter_name(
            Parse._extract_value(item, 'author.nickname'),
            default='无效账号昵称')
        account.mark = cleaner.filter_name(
            account.mark, default=account.name)

    @staticmethod
    def _extract_common(item: dict, result: dict, settings: Settings, cleaner: Cleaner):
        '''提取图文/视频作品共有信息'''
        result['id'] = Parse._extract_value(item, 'aweme_id')
        if desc:=Parse._extract_value(item, 'desc'):
            result['desc'] = cleaner.clear_spaces(cleaner.filter_name(desc))[:settings.file_description_max_length]
        else:
            result['desc'] = '作品描述为空'
        result['create_timestamp'] = Parse._extract_value(item, 'create_time')
        result['create_time_date'] = date.fromtimestamp(int(result['create_timestamp']))
        result['create_time'] = date.strftime(result['create_time_date'], settings.date_format)

    @staticmethod
    def _extract_gallery(gallery: dict, result: dict):
        '''提取图文作品信息'''
        result['type'] = '图集'
        result['share_url'] = f'https://www.douyin.com/note/{result["id"]}'
        result['downloads'] = []
        for image in gallery:
            url = Parse._extract_value(image, 'url_list[0]')
            width = Parse._extract_value(image, 'width')
            height = Parse._extract_value(image, 'height')
            result['downloads'].append((url, width, height))

    @staticmethod
    def _extract_video( video: dict, result: dict):
        '''提取视频作品信息'''
        result['type'] = '视频'
        result['format'] = '.'+Parse._extract_value(video, 'format')
        result['share_url'] = f'https://www.douyin.com/video/{result["id"]}'
        result['downloads'] = Parse._extract_value(
            video, 'play_addr.url_list[0]')
        result['height'] = Parse._extract_value(video, 'height')
        result['width'] = Parse._extract_value(video, 'width')

    @staticmethod
    def extract_items(items: list[dict], earliest: date, latest: date, settings: Settings, cleaner: Cleaner):
        '''提取发布作品信息并返回'''
        results = []
        for item in items:
            result = {}
            Parse._extract_common(item, result, settings, cleaner)
            if (result['create_time_date'] <= latest) and (result['create_time_date'] >= earliest):
                if (gallery := Parse._extract_value(item, 'images')):
                    if settings.download_images:
                        Parse._extract_gallery(gallery, result)
                        results.append(result)
                elif settings.download_videos:
                    Parse._extract_video(Parse._extract_value(item, 'video'), result)
                    results.append(result)
        return results
