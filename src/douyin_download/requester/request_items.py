import random
import time
from datetime import UTC
from datetime import date as Date
from datetime import datetime as Datetime
from urllib.parse import quote, urlencode

from requests import Session
from rich import print
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from douyin_download.config.constant import REFERER, USER_AGENT, Colors
from douyin_download.config.cookies import CookiesManager
from douyin_download.config.settings import Account
from douyin_download.encrypt_params import ABogus
from douyin_download.encrypt_params import normalize_query as websign_normalize_query
from douyin_download.encrypt_params import sign as web_sign
from douyin_download.utils import retry

__all__ = ["RequestItems", "SessionManager"]

POST_API = "https://www.douyin.com/aweme/v1/web/aweme/post/"


class SessionManager:
    def __init__(self, cookies: CookiesManager):
        self.cookies = cookies
        self.session = None

    def __enter__(self):
        self.session = Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.session.cookies.update(self.cookies.cookies)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

    def update_cookies(self) -> None:
        self.session.cookies.update(self.cookies.cookies)


class RequestItems:
    def __init__(
        self,
        timeout: int,
        cookies: CookiesManager,
        session: SessionManager,
        abogus: ABogus,
    ):
        self.timeout = timeout
        self.cookies = cookies
        self.session = session
        self.abogus = abogus
        self.params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "update_version_code": "170400",
            "pc_client_type": "1",
            "pc_libra_divert": "Mac",
            "support_h265": "1",
            "support_dash": "1",
            "version_code": "290100",
            "version_name": "29.1.0",
            "cookie_enabled": "true",
            "screen_width": "1536",
            "screen_height": "864",
            "browser_language": "zh-CN",
            "browser_platform": "MacIntel",
            "browser_name": "Chrome",
            "browser_version": "146.0.0.0",
            "browser_online": "true",
            "engine_name": "Blink",
            "engine_version": "146.0.0.0",
            "os_name": "Mac OS",
            "os_version": "10.15.7",
            "cpu_core_num": "16",
            "device_memory": "8",
            "platform": "PC",
            "downlink": "10",
            "effective_type": "4g",
            "round_trip_time": "200",
            "uifid": cookies.cookies["UIFID"],
            "msToken": "",
        }

    def run(self, account: Account) -> list[dict]:
        """获取账号作品数据并返回"""
        self.session.session.headers["Referer"] = f"{REFERER}user/{account.sec_user_id}"
        items = []
        with self._progress_object() as progress:
            progress.add_task("正在获取账号主页数据", total=None)
            cursor = 0
            while True:
                if not (
                    result := self._request_items_page_cursor_has_more(
                        account.sec_user_id, cursor
                    )
                ):
                    break
                items_page, cursor, has_more = result
                items.extend(items_page)
                if not has_more or self._early_stop_by_date(account.earliest, cursor):
                    break
        return items

    @staticmethod
    def _progress_object():
        return Progress(
            TextColumn(
                "[progress.description]{task.description}",
                style=Colors.MAGENTA,
                justify="left",
            ),
            "•",
            BarColumn(bar_width=20),
            "•",
            TimeElapsedColumn(),
            transient=True,
        )

    @retry
    def _request_items_page_cursor_has_more(self, sec_user_id: str, cursor: int):
        params = self.params | {
            "sec_user_id": sec_user_id,
            "max_cursor": cursor,
            "locate_query": "false",
            "show_live_replay_strategy": "1",
            "need_time_list": "1",
            "time_list_query": "0",
            "whale_cut_token": "",
            "cut_version": "1",
            "count": "18",
            "publish_video_strategy_type": "2",
            "from_user_page": "1",
        }
        query = self._deal_url_params(params)
        if not (data := self._send_get(query)):
            print(f"[{Colors.YELLOW}]获取账号作品数据失败")
            return None
        try:
            if (items_page := data["aweme_list"]) is None:
                print(
                    f"[{Colors.YELLOW}]该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号"
                )
                return None
            has_more = bool(data["has_more"])
            return items_page, data["max_cursor"], has_more
        except KeyError:
            print(f"[{Colors.YELLOW}]账号作品数据响应内容异常: {data}")
            return None

    def _deal_url_params(self, params: dict[str, str]):
        if "msToken" in self.cookies.cookies:
            params["msToken"] = self.cookies.cookies["msToken"]

        uifid = params["uifid"]
        query = websign_normalize_query(urlencode(params, doseq=True))

        a_bogus = self.abogus.get_value(query, body="")
        signed_query = f"{query}&a_bogus={quote(a_bogus, safe='')}"

        return web_sign(signed_query, uifid)[0]

    def _send_get(self, query: str):
        """返回 json 格式数据"""
        try:
            response = self.session.session.get(
                f"{POST_API}?{query}", timeout=self.timeout
            )
            time.sleep(random.uniform(1, 5))
        except Exception as e:  # noqa: BLE001
            print(f"[{Colors.YELLOW}]请求 {POST_API}?{query} 出错: {e}")
            return None
        try:
            return response.json()
        except Exception as e:  # noqa: BLE001
            print(f"[{Colors.YELLOW}]响应内容出错: {e}")
            return None

    def _early_stop_by_date(self, earliest: Date, cursor: int):
        return Datetime.fromtimestamp(cursor / 1000, tz=UTC).date() < earliest
