from datetime import date as Date
from urllib.parse import urlencode
from requests import Session, exceptions
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
import random
import time
from rich import print
from collections.abc import Mapping

from douyin_download.encrypt_params.js_port import get_a_bogus
from douyin_download.tool.function import retry
from douyin_download.config.constant import Colors, USER_AGENT, REFERER
from douyin_download.config.models import Settings
from douyin_download.config.cookies import Cookies


POST_API = 'https://www.douyin.com/aweme/v1/web/aweme/post/'


class RequestItems():
    def __init__(self, settings: Settings, cookies: Cookies):
        self.settings = settings
        self.cookies = cookies
        self.session = None

    def __enter__(self):
        self.session = Session()
        self.session.headers.update({'User-Agent': USER_AGENT, 'Referer': REFERER})
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

    def run(self, sec_user_id: str, earliest_date: Date) -> list[dict]:
        '''获取账号作品数据并返回'''
        self.session.cookies.update(self.cookies.cookies)
        items = []
        with self._progress_object() as progress:
            progress.add_task('正在获取账号主页数据', total=None)
            cursor = 0
            while True:
                if not (result := self._request_items_page_cursor_has_more(sec_user_id, cursor)):
                    break
                items_page, cursor, has_more = result
                items.extend(items_page)
                if not has_more or self._early_stop(earliest_date, cursor):
                    break
        return items

    @staticmethod
    def _progress_object() -> Progress:
        return Progress(
            TextColumn('[progress.description]{task.description}', style=Colors.MAGENTA, justify='left'),
            '•',
            BarColumn(bar_width=20),
            '•',
            TimeElapsedColumn(),
            transient=True,
        )

    def _deal_url_params(self, params: Mapping[str, str], number: int = 8) -> None:
        '''添加 msToken、X-Bogus'''
        if 'msToken' in self.cookies.cookies:
            params['msToken'] = self.cookies.cookies['msToken']
        params['a_bogus'] = get_a_bogus(params)

    @staticmethod
    def _wait() -> None:
        time.sleep(random.randint(15, 45) / 10)

    def _send_get(self, params: Mapping[str, str]) -> dict | None:
        '''返回 json 格式数据'''
        try:
            response = self.session.get(
                POST_API,
                params=params,
                timeout=self.settings.timeout,
            )
            self._wait()
        except (
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(params)} 失败')
            return None
        except exceptions.ReadTimeout:
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(params)} 超时')
            return None
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                print(f'[{Colors.YELLOW}]响应内容不是有效的 JSON 格式：{response.text}')
            else:
                print(f'[{Colors.YELLOW}]响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie')

    @retry
    def _request_items_page_cursor_has_more(self, sec_user_id: str, cursor: int) -> tuple[list[dict], int, bool] | None:
        params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'sec_user_id': sec_user_id,
            'max_cursor': cursor,
            'locate_query': 'false',
            'show_live_replay_strategy': '1',
            'need_time_list': '0' if cursor else '1',
            'time_list_query': '0',
            'whale_cut_token': '',
            'cut_version': '1',
            'count': '18',
            'publish_video_strategy_type': '2',
            'pc_client_type': '1',
            'version_code': '170400',
            'version_name': '17.4.0',
            'cookie_enabled': 'true',
            'platform': 'PC',
            'downlink': '10',
        }
        self._deal_url_params(params)
        if not (data := self._send_get(params)):
            print(f'[{Colors.YELLOW}]获取账号作品数据失败')
            return None
        try:
            if (items_page := data['aweme_list']) is None:
                print(f'[{Colors.YELLOW}]该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号')
                return None
            return items_page, data['max_cursor'], data['has_more']
        except KeyError:
            print(f'[{Colors.YELLOW}]账号作品数据响应内容异常: {data}')
            return None

    def _early_stop(self, earliest_date: Date, cursor: int) -> bool:
        '''如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了'''
        if earliest_date > Date.fromtimestamp(cursor / 1000):
            return True
        return False
