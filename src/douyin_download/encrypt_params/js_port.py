from urllib import parse
from py_mini_racer import MiniRacer
from pathlib import Path

from douyin_download.config.constant import USER_AGENT

__all__ = ["get_a_bogus"]

js_file = Path(__file__).resolve().with_name("a_bogus.js")


def get_a_bogus(query: dict):
    with open(js_file, "r", encoding="utf-8") as f:
        a_bogus_js_code = f.read()
    a_bogus_ctx = MiniRacer()
    a_bogus_ctx.eval(a_bogus_js_code)
    query = parse.unquote(parse.urlencode(query))
    a_bogus = a_bogus_ctx.call("generate_a_bogus", query, USER_AGENT)
    return a_bogus
