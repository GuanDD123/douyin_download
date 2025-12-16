from re import finditer
from rich import print
from json import load, dump

from .settings import Colors, PROJECT_ROOT, ENCODE
from ..encrypt_params import MsToken, TtWid


class Cookie:
    def __init__(self):
        self.cookies = {}

    def load_cookies(self):
        with open(PROJECT_ROOT / 'cookies.json', 'r', encoding=ENCODE) as f:
            self.cookies = load(f)

    @staticmethod
    def _generate_dict(cookie: str) -> dict:
        cookies_key = {
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
        }
        cookies = {}.fromkeys(cookies_key)
        matches = finditer(r'(?P<key>[^=;,]+)=(?P<value>[^;,]+)', cookie)
        for match in matches:
            key = match.group('key').strip()
            value = match.group('value').strip()
            if key in cookies_key:
                cookies[key] = value
        return cookies

    def _check(self) -> None:
        if not self.cookies['sessionid_ss']:
            print(f'[{Colors.CYAN}]当前 Cookie 未登录')
        else:
            print(f'[{Colors.CYAN}]当前 Cookie 已登录')

        keys_to_remove = [key for key, value in self.cookies.items() if value is None]
        for key in keys_to_remove:
            del self.cookies[key]

    def _save_json(self) -> None:
        with open(PROJECT_ROOT / 'cookies.json', 'w', encoding=ENCODE) as f:
            dump(self.cookies, f, ensure_ascii=False, indent=4)
        print(f'[{Colors.GREEN}]写入 Cookie 成功！')

    def input_save(self) -> None:
        while not (cookie := input(f'请粘贴 Cookie 内容: ')):
            continue
        self.cookies = self._generate_dict(cookie)
        self._check()
        self._save_json()

    def update(self) -> None:
        parameters = (MsToken.get_real_ms_token(), TtWid.get_tt_wid())
        for i in parameters:
            if isinstance(i, dict):
                self.cookies |= i

    def _generate_str(self) -> str:
        result = [f'{k}={v}' for k, v in self.cookies.items()]
        return '; '.join(result)
