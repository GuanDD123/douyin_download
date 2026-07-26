from json import dumps

from requests import exceptions
from rich import print

from douyin_download.config.constant import USER_AGENT, Colors

from .general import send_post


def get_web_id(user_agent: str = USER_AGENT):
    api = "https://mcs.zijieapi.com/webid"
    headers = {"User-Agent": user_agent}
    data = {
        "app_id": 6383,
        "url": "https://www.douyin.com/",
        "user_agent": "{user_agent}",
        "referer": "https://www.douyin.com/",
        "user_unique_id": "",
    }
    try:
        if response := send_post(api, headers, dumps(data)):
            return response.json().get("web_id")
        raise KeyError
    except (exceptions.JSONDecodeError, KeyError):
        print(f"[{Colors.RED}]获取 webid 参数失败！")
