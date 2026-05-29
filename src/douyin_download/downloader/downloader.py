from rich.progress import (SpinnerColumn, BarColumn, DownloadColumn, Progress,
                           TextColumn, TimeRemainingColumn)
from rich import print
from yarl import URL
from asyncio import Semaphore, gather, create_task, TimeoutError
from aiohttp import ClientSession, ClientResponse, ClientTimeout
from collections.abc import Sequence
from typing import Literal

from douyin_download.config.constant import Colors, USER_AGENT, REFERER
from douyin_download.config.models import Settings
from douyin_download.config.cookies import Cookies
from douyin_download.tool.function import retry_async
from douyin_download.parser.models import DownloadInfo


class Downloader:
    def __init__(self, settings: Settings, cookies: Cookies) -> None:
        self.settings = settings
        self.cookies = cookies
        self.session = None

    async def __aenter__(self):
        self.session = ClientSession(
            headers={'User-Agent': USER_AGENT, 'Referer': REFERER},
            timeout=ClientTimeout(self.settings.timeout))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def run(self, download_infos: Sequence[DownloadInfo]) -> None:
        '''下载作品文件'''
        self.session.cookie_jar.update_cookies(self.cookies.cookies)

        print(f'[{Colors.CYAN}]\n开始下载作品文件\n')
        sem = Semaphore(self.settings.concurrency)
        with self._progress_object() as progress:
            tasks = []
            for download_info in download_infos:
                if download_info.path.exists() and download_info.path.stat().st_size == download_info.data_size:
                    print(f'[{Colors.CYAN}]{download_info.path.name} 文件已存在且大小匹配，跳过下载')
                else:
                    task = create_task(self._request_file(download_info, sem, progress))
                    tasks.append(task)
            await gather(*tasks)

    @staticmethod
    def _progress_object():
        return Progress(
            TextColumn('[progress.description]{task.description}', style=Colors.MAGENTA, justify='left'),
            SpinnerColumn(),
            BarColumn(bar_width=20),
            '[progress.percentage]{task.percentage:>3.1f}%',
            '•',
            DownloadColumn(binary_units=True),
            '•',
            TimeRemainingColumn(),
            transient=True,
        )

    @retry_async
    async def _request_file(self, download_info: DownloadInfo, sem: Semaphore,
                            progress: Progress) -> Literal[True] | None:
        '''下载 url 对应文件'''
        async with sem:
            try:
                async with self.session.get(URL(download_info.url, encoded=True)) as response:
                    if not (content_length := int(response.headers.get('content-length', 0))):
                        print(f'[{Colors.YELLOW}]{download_info.path.name} {download_info.url} 响应内容为空')
                    elif response.status != 200 and response.status != 206:
                        print(f'[{Colors.YELLOW}]{download_info.path.name} {download_info.url} 响应状态码异常 {response.status}')
                    else:
                        await self._save_file(download_info, response, content_length, progress)
                        return True
            except TimeoutError:
                print(f'[{Colors.YELLOW}]{download_info.path.name} {download_info.url} 响应超时')
                return None

    async def _save_file(self, download_info: DownloadInfo, response: ClientResponse,
                         content_length: int, progress: Progress):
        task_id = progress.add_task(download_info.path.name, total=content_length or None)
        with open(download_info.path, 'wb') as f:
            async for chunk in response.content.iter_chunked(self.settings.chunk_size):
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))
        progress.remove_task(task_id)
        if max(download_info.width, download_info.height) < 1920:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        print(f'[{Colors.GREEN}]{download_info.path.name} [{color}]清晰度：'
              f'{download_info.width}×{download_info.height}[{Colors.GREEN}] 下载完成 '
              f'({download_info.path.stat().st_size / (1024 * 1024):.2f} MB)')
