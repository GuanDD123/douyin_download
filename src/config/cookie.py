from re import finditer
from browser_cookie3 import (
    chrome,
    chromium,
    opera,
    opera_gx,
    brave,
    edge,
    vivaldi,
    firefox,
    librewolf,
    safari,
    BrowserCookieError,
)
from http.cookiejar import CookieJar

from .constant import WARNING, INFO
from .settings import Settings
from tool import ColorfulConsole
from encrypt_params import MsToken, TtWid


class Cookie:
    '''browser_cookie 代码参考：https://github.com/Johnserf-Seed/f2/blob/main/f2/apps/douyin/cli.py'''

    def __init__(self, settings: Settings, console: ColorfulConsole) -> None:
        self.settings = settings
        self.console = console

    def input_save(self):
        '''输入 cookie，转为 dict，保存到 Settings.cookies 属性中，并存入配置文件'''
        while not (cookie := self.console.input('请粘贴 Cookie 内容: ')):
            continue
        self.settings.cookies = self.__generate_dict_str(cookie)
        self.__check()
        self.__save()

    def __check(self):
        '''检查 Settings.cookies 是否已登录；删除空键值对'''
        cookies = self.settings.cookies
        if not cookies['sessionid_ss']:
            self.console.print('当前 Cookie 未登录')
        else:
            self.console.print('当前 Cookie 已登录')
        keys_to_remove = [key for key, value in cookies.items() if value is None]
        for key in keys_to_remove:
            del cookies[key]

    def __save(self):
        '''将 Settings.cookies 存储到 settings.json'''
        self.settings.save()
        self.console.print('写入 Cookie 成功！', style=INFO)

    def update(self):
        '''更新 Settings.cookies 与 Settings.headers'''
        if self.settings.cookies:
            self.__add_cookies()
            self.settings.headers['Cookie'] = self.__generate_str(self.settings.cookies)

    def __add_cookies(self):
        parameters = (MsToken.get_real_ms_token(), TtWid.get_tt_wid())
        for i in parameters:
            if isinstance(i, dict):
                self.settings.cookies |= i

    def browser_save(self):
        '从指定浏览器获取 cookiejar，转为 dict，保存到 Settings.cookies，并存入配置文件'
        browser_allow = (chrome, chromium, opera, opera_gx, brave, edge, vivaldi, firefox, librewolf, safari)
        browser = self.console.input(
            '自动读取指定浏览器的 Cookie 并写入配置文件\n'
            '支持浏览器：1 Chrome, 2 Chromium, 3 Opera, 4 Opera GX, 5 Brave, 6 Edge, 7 Vivaldi, 8 Firefox, 9 LibreWolf, 10 Safari\n'
            '请先关闭对应的浏览器，然后输入浏览器序号：')
        try:
            cookie = browser_allow[int(browser) - 1](domain_name='douyin.com')
            self.settings.cookies = self.__generate_dict_cookiejar(cookie)
            self.__check()
            self.__save()
        except ValueError:
            self.console.print('浏览器序号错误，未写入 Cookie！', style=WARNING)
        except PermissionError:
            self.console.print(
                '获取 Cookie 失败，请先关闭对应的浏览器，然后输入浏览器序号！',
                style=WARNING)
        except BrowserCookieError:
            self.console.print(
                '获取 Cookie 失败，未找到对应浏览器的 Cookie 数据！',
                style=WARNING)

    @staticmethod
    def __generate_str(cookies: dict):
        '''根据 dict 生成 str'''
        if cookies:
            result = [f'{k}={v}' for k, v in cookies.items()]
            return '; '.join(result)

    @staticmethod
    def __generate_dict_str(cookie: str):
        '''根据 str 生成 dict'''
        cookies_key = frozenset({
            'passport_csrf_token',
            'passport_csrf_token_default',
            'my_rd',
            'passport_auth_status',
            'passport_auth_status_ss',
            'd_ticket',
            'publish_badge_show_info',
            'volume_info',
            '__live_version__',
            'download_guide',
            'EnhanceDownloadGuide',
            'pwa2',
            'live_can_add_dy_2_desktop',
            'live_use_vvc',
            'store-region',
            'store-region-src',
            'strategyABtestKey',
            'FORCE_LOGIN',
            'LOGIN_STATUS',
            '__security_server_data_status',
            '_bd_ticket_crypt_doamin',
            'n_mh',
            'passport_assist_user',
            'sid_ucp_sso_v1',
            'ssid_ucp_sso_v1',
            'sso_uid_tt',
            'sso_uid_tt_ss',
            'toutiao_sso_user',
            'toutiao_sso_user_ss',
            'sessionid',
            'sessionid_ss',
            'sid_guard',
            'sid_tt',
            'sid_ucp_v1',
            'ssid_ucp_v1',
            'uid_tt',
            'uid_tt_ss',
            'FOLLOW_NUMBER_YELLOW_POINT_INFO',
            'vdg_s',
            '_bd_ticket_crypt_cookie',
            'FOLLOW_LIVE_POINT_INFO',
            'bd_ticket_guard_client_data',
            'bd_ticket_guard_client_web_domain',
            'home_can_add_dy_2_desktop',
            'odin_tt',
            'stream_recommend_feed_params',
            'IsDouyinActive',
            'stream_player_status_params',
            's_v_web_id',
            '__ac_nonce',
            'dy_sheight',
            'dy_swidth',
            'ttcid',
            'xgplayer_user_id',
            '__ac_signature',
            'tt_scid'
        })
        cookies = {}.fromkeys(cookies_key)
        matches = finditer(r'(?P<key>[^=;,]+)=(?P<value>[^;,]+)', cookie)
        for match in matches:
            key = match.group('key').strip()
            value = match.group('value').strip()
            if key in cookies_key:
                cookies[key] = value
        return cookies

    @staticmethod
    def __generate_dict_cookiejar(cookie: CookieJar):
        '''根据 cookiejar 生成 dict'''
        return {i.name: i.value for i in cookie}