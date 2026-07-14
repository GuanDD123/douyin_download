from datetime import date as Date

from douyin_download.config.settings import Settings, Account
from douyin_download.models import AccountInfo
from .models import ItemInfo
from .utils import filter_name, clear_spaces


def _extract_value(data: dict, attribute_chain: str):
    """根据 attribute_chain 从 dict 中提取值"""
    attributes = attribute_chain.split(".")
    for attribute in attributes:
        if "[" in attribute:
            parts = attribute.split("[", 1)
            attribute = parts[0]
            index = int(parts[1].split("]", 1)[0])
            data = data[attribute][index]
        else:
            data = data[attribute]
        if not data:
            return None
    return data


def extract_account_info(
    mark: str, item: dict, illegal_char: set[str]
) -> AccountInfo:
    """提取账号 id、昵称，规范化账号 mark"""
    id = _extract_value(item, "author.uid")
    name = filter_name(
        _extract_value(item, "author.nickname"),
        illegal_char=illegal_char,
        default="无效账号昵称",
    )
    mark = filter_name(mark, illegal_char=illegal_char, default=name)
    return AccountInfo(id=id, name=name, mark=mark)


def _extract_common_info(item: dict, settings: Settings):
    result = {}
    result["id"] = _extract_value(item, "aweme_id")
    if desc := _extract_value(item, "desc"):
        result["desc"] = clear_spaces(filter_name(desc, settings.illegal_char))[
            : settings.file_description_max_length
        ]
    else:
        result["desc"] = "作品描述为空"
    result["create_timestamp"] = _extract_value(item, "create_time")
    result["create_time"] = Date.fromtimestamp(int(result["create_timestamp"]))
    return result


def _extract_image_infos(images: dict, result: dict):
    results: list[ItemInfo] = []
    result["type"] = "image"
    result["share_url"] = f"https://www.douyin.com/note/{result['id']}"
    for index, image in enumerate(images):
        result["index"] = index
        result["url"] = _extract_value(image, "url_list[0]")
        result["width"] = _extract_value(image, "width")
        result["height"] = _extract_value(image, "height")
        results.append(ItemInfo(**result, format=None, data_size=None))
    return results


def _extract_video_info(video: dict, result: dict, settings: Settings):
    result["type"] = "video"
    result["format"] = "." + _extract_value(video, "format")
    result["share_url"] = f"https://www.douyin.com/video/{result['id']}"
    result["url"] = _extract_value(video, "play_addr.url_list[0]")
    result["width"] = _extract_value(video, "play_addr.width")
    result["height"] = _extract_value(video, "play_addr.height")
    result["data_size"] = _extract_value(video, "play_addr.data_size")
    if not settings.download_horizontal_video and result["width"] > result["height"]:
        return None
    if not settings.download_vertical_video and result["width"] < result["height"]:
        return None
    return ItemInfo(**result, index=None)


def extract_item_infos(
    items: list[dict], settings: Settings, account: Account
) -> list[ItemInfo]:
    item_infos = []
    for item in items:
        result = _extract_common_info(item, settings)
        if (result["create_time"] > account.latest) or (
            result["create_time"] < account.earliest
        ):
            continue
        if images := _extract_value(item, "images"):
            if settings.download_images:
                if image_infos := _extract_image_infos(images, result):
                    item_infos.extend(image_infos)
        elif video := _extract_value(item, "video"):
            if settings.download_videos:
                if video_info := _extract_video_info(video, result, settings):
                    item_infos.append(video_info)
    return item_infos
