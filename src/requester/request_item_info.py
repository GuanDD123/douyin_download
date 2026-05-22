from datetime import date as Date
from urllib.parse import urlencode
from requests import Session, exceptions
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
import random
import time
from rich import print
from collections.abc import Mapping

from src.encrypt_params.js_port import get_a_bogus
from src.tool.function import retry
from src.config.constant import Colors, USER_AGENT, REFERER
from src.config.models import Account, Settings
from src.config.cookies import Cookies


POST_API = 'https://www.douyin.com/aweme/v1/web/aweme/post/'


class RequestItems():
    def __init__(self, settings: Settings, cookies: Cookies, account: Account):
        self.settings = settings
        self.cookies = cookies
        self.account = account
        self.session = None
        self.progress: Progress = None
        self.cursor: int = None
        self.finished: bool = None
        self.params: Mapping[str, str] = None

    def __enter__(self):
        self.session = Session()
        self.session.headers.update({'User-Agent': USER_AGENT, 'Referer': REFERER})
        self.session.cookies.update(self.cookies.cookies)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.session.close()

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

    def _deal_url_params(self, number: int = 8) -> None:
        '''添加 msToken、X-Bogus'''
        if 'msToken' in self.cookies.cookies:
            self.params['msToken'] = self.cookies.cookies['msToken']
        self.params['a_bogus'] = get_a_bogus(self.params)

    @staticmethod
    def _wait() -> None:
        time.sleep(random.randint(15, 45) / 10)

    def _send_get(self) -> dict | None:
        '''返回 json 格式数据'''
        try:
            response = self.session.get(
                POST_API,
                params=self.params,
                timeout=self.settings.timeout,
            )
            self._wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(self.params)} 失败')
            return
        except exceptions.ReadTimeout:
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(self.params)} 超时')
            return
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                print(f'[{Colors.YELLOW}]响应内容不是有效的 JSON 格式：{response.text}')
            else:
                print(f'[{Colors.YELLOW}]响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie')

    @retry
    def _request_items_page(self) -> list[dict] | None:
        '''获取单页作品数据，更新 self.cursor'''
        self.params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'sec_user_id': self.account.sec_user_id,
            'max_cursor': self.cursor,
            'locate_query': 'false',
            'show_live_replay_strategy': '1',
            'need_time_list': '0' if self.cursor else '1',
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
        self._deal_url_params()
        if not (data := self._send_get()):
            print(f'[{Colors.YELLOW}]获取账号作品数据失败')
            self.finished = True
        else:
            try:
                if (items_page := data['aweme_list']) is None:
                    print(f'[{Colors.YELLOW}]该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号')
                    self.finished = True
                else:
                    self.cursor = data['max_cursor']
                    self.finished = not data['has_more']
                    return items_page or [None]
            except KeyError:
                print(f'[{Colors.YELLOW}]账号作品数据响应内容异常: {data}')
                self.finished = True

    def _early_stop(self) -> None:
        '''如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了'''
        if self.account.earliest_date > Date.fromtimestamp(self.cursor / 1000):
            self.finished = True

    def run(self) -> list[dict]:
        '''获取账号作品数据并返回'''
        items = []
        with self._progress_object() as self.progress:
            self.progress.add_task('正在获取账号主页数据', total=None)
            self.cursor = 0
            self.finished = False
            while not self.finished:
                if (items_page := self._request_items_page()):
                    if not items_page == [None]:
                        items.extend(items_page)
                    self._early_stop()
        return items
