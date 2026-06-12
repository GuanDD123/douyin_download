from datetime import date as Date
from urllib.parse import urlencode
from requests import Session
from rich import print
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
import random
import time

from douyin_download.encrypt_params.js_port import get_a_bogus
from douyin_download.tool.retry import retry
from douyin_download.config.constant import Colors, USER_AGENT, REFERER
from douyin_download.config.models import Account
from douyin_download.config.cookies import CookiesManager


POST_API = "https://www.douyin.com/aweme/v1/web/aweme/post/"


class SessionManager:
    def __init__(self, cookies_manager: CookiesManager):
        self.cookies_manager = cookies_manager
        self.session = None

    def __enter__(self):
        self.session = Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Referer": REFERER})
        self.session.cookies.update(self.cookies_manager.cookies)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

    def update_cookies(self) -> None:
        self.session.cookies.update(self.cookies_manager.cookies)


class RequestItemInfo:
    def __init__(
        self,
        timeout: int,
        cookies_manager: CookiesManager,
        session_manager: SessionManager,
    ):
        self.timeout = timeout
        self.cookies_manager = cookies_manager
        self.session_manager = session_manager

    def run(self, account: Account) -> list[dict]:
        """获取账号作品数据并返回"""
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
                if not has_more or self._early_stop_by_date(
                    account.earliest_date, cursor
                ):
                    break
        return items

    @staticmethod
    def _progress_object() -> Progress:
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
    def _request_items_page_cursor_has_more(
        self, sec_user_id: str, cursor: int
    ) -> tuple[list[dict], int, bool] | None:
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": sec_user_id,
            "max_cursor": cursor,
            "locate_query": "false",
            "show_live_replay_strategy": "1",
            "need_time_list": "0" if cursor else "1",
            "time_list_query": "0",
            "whale_cut_token": "",
            "cut_version": "1",
            "count": "18",
            "publish_video_strategy_type": "2",
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }
        self._deal_url_params(params)
        if not (data := self._send_get(params)):
            print(f"[{Colors.YELLOW}]获取账号作品数据失败")
            return None
        try:
            if (items_page := data["aweme_list"]) is None:
                print(
                    f"[{Colors.YELLOW}]该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号"
                )
                return None
            has_more = True if data["has_more"] else False
            return items_page, data["max_cursor"], has_more
        except KeyError:
            print(f"[{Colors.YELLOW}]账号作品数据响应内容异常: {data}")
            return None

    def _deal_url_params(self, params: dict[str, str], number: int = 8) -> None:
        """添加 msToken、X-Bogus"""
        if "msToken" in self.cookies_manager.cookies:
            params["msToken"] = self.cookies_manager.cookies["msToken"]
        params["a_bogus"] = get_a_bogus(params)

    def _send_get(self, params: dict[str, str]) -> dict | None:
        """返回 json 格式数据"""
        try:
            response = self.session_manager.session.get(
                POST_API, params=params, timeout=self.timeout
            )
            time.sleep(random.uniform(1, 5))
        except Exception as e:
            print(f"[{Colors.YELLOW}]请求 {POST_API}?{urlencode(params)} 出错: {e}")
            return None
        try:
            return response.json()
        except Exception as e:
            print(f"[{Colors.YELLOW}]响应内容出错: {e}")
            return None

    def _early_stop_by_date(self, earliest_date: Date, cursor: int) -> bool:
        if Date.fromtimestamp(cursor / 1000) < earliest_date:
            return True
        return False
