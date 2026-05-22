from rich.progress import (SpinnerColumn, BarColumn, DownloadColumn, Progress,
                           TextColumn, TimeRemainingColumn)
from rich import print
from yarl import URL
from asyncio import Semaphore, gather, create_task, TimeoutError
from aiohttp import ClientSession, ClientResponse, ClientTimeout
from collections.abc import Sequence

from src.config.constant import Colors, USER_AGENT, REFERER
from src.config.models import Settings
from src.config.cookies import Cookies
from src.tool.function import retry_async
from src.parser.models import DownloadInfo


class Downloader:
    def __init__(self, settings: Settings, cookies: Cookies, download_infos: Sequence[DownloadInfo]) -> None:
        self.settings = settings
        self.cookies = cookies
        self.download_infos = download_infos
        self.session = None
        self.progress: Progress = None
        self.sem: Semaphore = None

    async def __aenter__(self):
        self.session = ClientSession(
            headers={'User-Agent': USER_AGENT, 'Referer': REFERER},
            timeout=ClientTimeout(self.settings.timeout),
            proxy=self.settings.proxy,
            cookies=self.cookies.cookies)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

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

    async def _save_file(self, download_info: DownloadInfo, response: ClientResponse,
                         content_length: int):
        task_id = self.progress.add_task(download_info.show, total=content_length or None)
        with open(download_info.path, 'wb') as f:
            async for chunk in response.content.iter_chunked(self.settings.chunk_size):
                f.write(chunk)
                self.progress.update(task_id, advance=len(chunk))
        self.progress.remove_task(task_id)
        if max(download_info.width, download_info.height) < 1920:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        print(f'[{Colors.GREEN}]{download_info.show} [{color}]清晰度：'\
              f'{download_info.width}×{download_info.height}[{Colors.GREEN}] 下载完成 '\
                 f'({download_info.path.stat().st_size / (1024 * 1024):.2f} MB)')

    @retry_async
    async def _request_file(self, download_info: DownloadInfo):
        '''下载 url 对应文件'''
        async with self.sem:
            try:
                async with self.session.get(URL(download_info.url, encoded=True)) as response:
                    if not (content_length := int(response.headers.get('content-length', 0))):
                        print(f'[{Colors.YELLOW}]{download_info.show} {download_info.url} 响应内容为空')
                    elif response.status != 200 and response.status != 206:
                        print(f'[{Colors.YELLOW}]{download_info.show} {download_info.url} 响应状态码异常 {response.status}')
                    else:
                        await self._save_file(download_info, response, content_length)
                        return True
            except TimeoutError:
                print(f'[{Colors.YELLOW}]{download_info.show} {download_info.url} 响应超时')

    async def run(self):
        '''下载作品文件'''
        print(f'[{Colors.CYAN}]\n开始下载作品文件\n')
        with self._progress_object() as self.progress:
            self.sem = Semaphore(self.settings.concurrency)
            tasks = []
            for download_info in self.download_infos:
                task = create_task(self._request_file(download_info))
                tasks.append(task)
            await gather(*tasks)
