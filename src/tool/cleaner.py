from platform import system
from string import whitespace
from rich import print

from ..config import Colors


class Cleaner:

    def __init__(self):
        '''替换字符串中包含的非法字符，
        默认根据系统类型生成对应的非法字符集合，也可以自行设置非法字符集合'''
        self.rule = self.generate_default_rule()

    @staticmethod
    def generate_default_rule() -> set[str]:
        '''根据系统类型生成默认非法字符集合'''
        now_system = system()
        if now_system in ('Windows', 'Darwin'):
            rule = {'/', '\\', '|', '<', '>', '\'', '\"', '?', ':', '*', '\x00'}  # Windows 系统和 Mac 系统
        elif now_system == 'Linux':
            rule = {'/', '\x00'}  # Linux 系统
        else:
            print(f'[{Colors.YELLOW}]不受支持的操作系统类型，可能无法正常去除非法字符！')
            rule = set()
        return rule | {i for i in whitespace[1:]}  # 补充换行符等非法字符

    def filter_name(self, text: str, default: str = ''):
        for i in self.rule:
            text = text.replace(i, ' ')
        text = text.strip().strip('.')

        return text or default

    @staticmethod
    def clear_spaces(string: str):
        '''将连续的空格转换为单个空格'''
        return ' '.join(string.split())
