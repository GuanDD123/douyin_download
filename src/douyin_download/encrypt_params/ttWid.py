from json import dumps

from .general import send_post, extract_value
from .general import HEADERS

__all__ = ["get_tt_wid"]

"""代码参考: https://github.com/Johnserf-Seed/f2/blob/main/f2/apps/douyin/utils.py"""


def get_tt_wid():
    api = "https://ttwid.bytedance.com/ttwid/union/register/"
    data = {
        "region": "cn",
        "aid": 1768,
        "needFid": "false",
        "service": "www.ixigua.com",
        "migrate_info": {"ticket": "", "source": "node"},
        "cbUrlProtocol": "https",
        "union": "true",
    }
    if response := send_post(api, HEADERS, dumps(data)):
        return extract_value(response.headers, "ttwid")
