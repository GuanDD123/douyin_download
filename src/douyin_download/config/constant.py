from pathlib import Path
import os
import re

PROJECT_ROOT = Path(__file__).parents[3]
ENCODE = "UTF-8-SIG" if os.name == "nt" else "UTF-8"
REFERER = "https://www.douyin.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PHONE_USER_AGENT = "com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36"
RETRY_ACCOUNT: int = 3
RETRY_DOWNLOAD: int = 2
URL_PATTERN = re.compile(r"(https://www\.douyin\.com/user/[A-Za-z0-9_-]+)(\?.*)?$")


class Colors:
    WHITE = "#aaaaaa"
    CYAN = "bright_cyan"
    RED = "bright_red"
    YELLOW = "bright_yellow"
    GREEN = "bright_green"
    MAGENTA = "bright_magenta"
