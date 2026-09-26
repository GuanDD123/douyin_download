import json
import re

from rich import print

from douyin_download.encrypt_params import get_real_ms_token, get_tt_wid

from .constant import ENCODE, PROJECT_ROOT, Colors


def _generate_dict(cookies_str: str):
    if not cookies_str:
        return {}
    cookies = {}
    matches = re.finditer(r"(?P<key>[^=;,]+)=(?P<value>[^;,]+)", cookies_str)
    for match in matches:
        key = match.group("key").strip()
        value = match.group("value").strip()
        cookies[key] = value
    return cookies


def _check(cookies: dict[str, str]):
    if not cookies["sessionid_ss"]:
        print(f"[{Colors.CYAN}]当前 Cookie 未登录")
    else:
        print(f"[{Colors.CYAN}]当前 Cookie 已登录")

    if not cookies.get("UIFID"):
        print("抖音 cookie 缺少 uifid 键值对，请尝试重新写入 cookie")

    keys_to_remove = [key for key, value in cookies.items() if value is None]
    for key in keys_to_remove:
        del cookies[key]


def _save_json(cookies: dict[str, str]):
    with open(PROJECT_ROOT / "cookies.json", "w", encoding=ENCODE) as f:
        json.dump(cookies, f, ensure_ascii=False, indent=4)
    print(f"[{Colors.GREEN}]写入 Cookie 成功！")


def input_save_cookies() -> None:
    while not (cookies_str := input("请粘贴 Cookie 内容: ")):
        continue
    cookies = _generate_dict(cookies_str)
    _check(cookies)
    _save_json(cookies)


class CookiesManager:
    def __init__(self):
        self.cookies: dict[str, str] = self._load_cookies()

    def _load_cookies(self):
        with open(PROJECT_ROOT / "cookies.json", "r", encoding=ENCODE) as f:
            return json.load(f)

    def update(self) -> None:
        parameters = (get_real_ms_token(), get_tt_wid())
        for i in parameters:
            if isinstance(i, dict):
                self.cookies |= i
