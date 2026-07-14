from rich import print
from rich.progress import (
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
from yarl import URL
import asyncio
from asyncio import Semaphore
from aiohttp import ClientResponse, ClientSession, ClientTimeout
from collections.abc import Callable, AsyncIterator
from pathlib import Path

from douyin_download.config.constant import Colors, USER_AGENT, REFERER, RETRY_DOWNLOAD
from douyin_download.config.cookies import CookiesManager
from douyin_download.models import DownloadInfo

__all__ = ["SessionManager", "DownloadMedia"]


def retry_async(function):
    """发生错误时尝试重新执行"""

    async def inner(*args, **kwargs):
        for _ in range(int(RETRY_DOWNLOAD) + 1):
            if result := await function(*args, **kwargs):
                return result
        return result

    return inner


class SessionManager:
    def __init__(self, timeout: int, cookies: CookiesManager):
        self.timeout = timeout
        self.cookies = cookies
        self.session = None

    async def __aenter__(self):
        self.session = ClientSession(
            headers={"User-Agent": USER_AGENT, "Referer": REFERER},
            timeout=ClientTimeout(self.timeout),
            cookies=self.cookies.cookies,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    def update_cookies(self) -> None:
        self.session.cookie_jar.update_cookies(self.cookies.cookies)


class DownloadMedia:
    def __init__(self, concurrency: int, session: SessionManager):
        self.sem = Semaphore(concurrency)
        self.session = session

    async def run(self, infos: list[DownloadInfo]) -> None:
        print(f"[{Colors.CYAN}]\n开始下载作品文件\n")
        with self._progress_object() as progress:
            tasks = []
            for info in infos:
                if info.path.exists() and info.path.stat().st_size == info.data_size:
                    print(
                        f"[{Colors.CYAN}]{info.path.name} 文件已存在且大小匹配，跳过下载"
                    )
                else:
                    task = asyncio.create_task(self._download(info, progress))
                    tasks.append(task)
            await asyncio.gather(*tasks)

    @staticmethod
    def _progress_object():
        return Progress(
            TextColumn(
                "[progress.description]{task.description}",
                style=Colors.MAGENTA,
                justify="left",
            ),
            SpinnerColumn(),
            BarColumn(bar_width=20),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(binary_units=True),
            "•",
            TimeRemainingColumn(),
            transient=True,
        )

    @retry_async
    async def _download(self, info: DownloadInfo, progress: Progress):
        async with self.sem:
            try:
                async with self.session.session.get(
                    URL(info.url, encoded=True)
                ) as response:
                    if not (
                        content_length := int(response.headers.get("content-length", 0))
                    ):
                        print(
                            f"[{Colors.YELLOW}]{info.path.name} {info.url} 响应内容为空"
                        )
                        return False
                    if response.status != 200 and response.status != 206:
                        print(
                            f"[{Colors.YELLOW}]{info.path.name} {info.url} 响应状态码异常 {response.status}"
                        )
                        return False

                    task_id = progress.add_task(
                        info.path.name, total=content_length or None
                    )

                    def update_progress(chunk_size: int):
                        progress.update(task_id, advance=chunk_size)

                    await self._write_file(
                        info.path, self._stream_body(response), update_progress
                    )

                    progress.remove_task(task_id)

                    self._show_media_info(info)
                    return True
            except Exception as e:
                print(f"[{Colors.RED}]下载失败: {info.path.name} - {e}")
                return False

    @staticmethod
    async def _write_file(
        path: Path, chunk_iter: AsyncIterator[bytes], on_progress: Callable
    ):
        with open(path, "wb") as f:
            async for chunk in chunk_iter:
                f.write(chunk)
                on_progress(len(chunk))

    @staticmethod
    async def _stream_body(response: ClientResponse):
        async for chunk in response.content.iter_chunked(1024 * 1024):
            yield chunk

    @staticmethod
    def _show_media_info(info: DownloadInfo):
        if max(info.width, info.height) < 1920:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        print(
            f"[{Colors.GREEN}]{info.path.name} [{color}]清晰度：{info.width}×{info.height}[{Colors.GREEN}] 下载完成 ({info.path.stat().st_size / (1024 * 1024):.2f} MB)"
        )
