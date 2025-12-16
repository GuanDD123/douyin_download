from datetime import date
from urllib.parse import urlencode
from requests import exceptions, get
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from random import randint
from time import sleep
from rich import print

from ..encrypt_params import get_a_bogus
from ..tool import retry
from ..config import Settings, Colors, Cookie, HEADERS

POST_API = 'https://www.douyin.com/aweme/v1/web/aweme/post/'

class Acquire():

    def __init__(self):
        self.cursor = 0
        self.finished = False

    @staticmethod
    def _progress_object():
        return Progress(
            TextColumn('[progress.description]{task.description}', style=Colors.MAGENTA, justify='left'),
            '•',
            BarColumn(bar_width=20),
            '•',
            TimeElapsedColumn(),
            transient=True,
        )

    @staticmethod
    def _deal_url_params(params: dict, cookie: Cookie, number: int = 8):
        '''添加 msToken、X-Bogus'''
        if 'msToken' in cookie.cookies:
            params['msToken'] = cookie.cookies['msToken']
        params['a_bogus'] = get_a_bogus(params)

    @staticmethod
    def _wait():
        sleep(randint(15, 45)/10)

    @staticmethod
    def _send_get(params, settings: Settings, cookie: Cookie):
        '''返回 json 格式数据'''
        try:
            headers = HEADERS | {'Cookie': cookie._generate_str()}
            response = get(
                POST_API,
                params=params,
                timeout=settings.timeout,
                headers=headers,
                )
            Acquire._wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(params)} 失败')
            return
        except exceptions.ReadTimeout:
            print(f'[{Colors.YELLOW}]网络异常，请求 {POST_API}?{urlencode(params)} 超时')
            return
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                print(f'[{Colors.YELLOW}]响应内容不是有效的 JSON 格式：{response.text}')
            else:
                print(f'[{Colors.YELLOW}]响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie')

    @retry
    def _request_items_page(self, sec_user_id: str, settings: Settings, cookie: Cookie):
        '''获取单页作品数据，更新 self.cursor'''
        params = {
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'sec_user_id': sec_user_id,
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
        self._deal_url_params(params, cookie)
        if not (data := self._send_get(params=params, settings=settings, cookie=cookie)):
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

    def _early_stop(self, earliest: date):
        '''如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了'''
        if earliest > date.fromtimestamp(self.cursor / 1000):
            self.finished = True

    def request_items(self, sec_user_id: str, earliest: date, settings: Settings, cookie: Cookie):
        '''获取账号作品数据并返回'''
        items = []
        with self._progress_object() as progress:
            progress.add_task('正在获取账号主页数据', total=None)
            self.cursor = 0
            self.finished = False
            while not self.finished:
                if (items_page := self._request_items_page(sec_user_id, settings, cookie)):
                    if not items_page == [None]:
                        items.extend(items_page)
                    self._early_stop(earliest)
        return items
