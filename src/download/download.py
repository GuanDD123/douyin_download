from rich.progress import (
    SpinnerColumn,
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)
from pathlib import Path
from rich import print
from yarl import URL
from asyncio import Semaphore, gather, run, create_task, TimeoutError
from aiohttp import ClientSession, ClientResponse, ClientTimeout

from ..config import Settings, Cookie, Colors, HEADERS
from ..tool import Cleaner, retry_async


class Download:
    @staticmethod
    def _create_save_folder(id: str, mark: str, settings: Settings):
        '''新建存储文件夹，返回文件夹路径'''
        folder = settings.save_folder / f'UID{id}_{mark}_发布作品'
        folder.mkdir(exist_ok=True)
        return folder

    @staticmethod
    def _generate_task_image(id: str, desc: str, name: str, index: int, url: str, width: int, height: int, save_folder: Path):
        '''生成图片下载任务信息'''
        show = f'图集 {id} {desc[:15]}'
        if (path := save_folder / f'{name}_{index}.jpeg').exists():
            print(f'[{Colors.CYAN}]{show} 文件已存在，跳过下载')
        else:
            return (url, path, show, id, width, height)

    @staticmethod
    def _generate_task_video(id: str, desc: str, name: str, format: str, url: str, width: int, height: int, save_folder: Path):
        '''生成视频下载任务信息'''
        show = f'视频 {id} {desc[:15]}'
        if (path := save_folder / f'{name}{format}').exists():
            print(f'[{Colors.CYAN}]{show} 文件已存在，跳过下载')
        else:
            return (url, path, show, id, width, height)

    @staticmethod
    def _generate_task(items: list[dict], save_folder: Path, settings: Settings, cleaner: Cleaner):
        '''生成下载任务信息列表并返回'''
        tasks = []
        for item in items:
            id = item['id']
            desc = item['desc']
            name = cleaner.filter_name(settings.split.join(
                item[key] for key in settings.name_format))
            format = item.get('format') # 图片任务解析时没有提取字段，在下面直接设置为 .jpeg
            if (type := item['type']) == '图集':
                for index, info in enumerate(item['downloads'], start=1):
                    if (task := Download._generate_task_image(
                        id, desc, name, index, info[0], info[1], info[2], save_folder)) is not None:
                        tasks.append(task)
            elif type == '视频':
                url = item['downloads']
                width = item['width']
                height = item['height']
                if (task := Download._generate_task_video(
                    id, desc, name, format, url, width, height, save_folder)) is not None:
                    tasks.append(task)
        return tasks

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

    @staticmethod
    async def _save_file(path: Path, show: str, id: str, width: int, height: int,
                         response: ClientResponse, content_length: int, progress: Progress, settings: Settings):
        task_id = progress.add_task(show, total=content_length or None)
        with open(path, 'wb') as f:
            async for chunk in response.content.iter_chunked(settings.chunk_size):
                f.write(chunk)
                progress.update(task_id, advance=len(chunk))
        progress.remove_task(task_id)
        if max(width, height) < 1920:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        print(f'[{Colors.GREEN}]{show} [{color}]清晰度：{width}×{height}[{Colors.GREEN}] 下载完成 ({path.stat().st_size / (1024 * 1024):.2f} MB)')

    @staticmethod
    @retry_async
    async def _request_file(url: str, path: Path, show: str, id: str, width: int, height: int,
                            progress: Progress, sem: Semaphore, settings: Settings, cookie: Cookie):
        '''下载 url 对应文件'''
        async with sem:
            try:
                async with ClientSession(
                    headers=HEADERS | {'Cookie': cookie._generate_str()},
                    timeout=ClientTimeout(settings.timeout),
                    proxy=settings.proxy,
                ) as session:
                    async with session.get(URL(url, encoded=True)) as response:
                        if not (content_length := int(response.headers.get('content-length', 0))):
                            print(f'[{Colors.YELLOW}]{show} {url} 响应内容为空')
                        elif response.status != 200 and response.status != 206:
                            print(f'[{Colors.YELLOW}]{show} {url} 响应状态码异常 {response.status}')
                        else:
                            await Download._save_file(path, show, id, width, height,
                                                      response, content_length, progress, settings)
                            return True
            except TimeoutError:
                print(f'[{Colors.YELLOW}]{show} {url} 响应超时')

    @staticmethod
    async def _download_file(task_info: tuple, progress: Progress, sem: Semaphore,
                             settings: Settings, cookie: Cookie):
        await Download._request_file(*task_info, progress, sem, settings, cookie)

    @staticmethod
    async def _download_files(tasks_info: list, progress: Progress, settings: Settings, cookie: Cookie):
        sem = Semaphore(settings.concurrency)
        tasks = []
        for task_info in tasks_info:
            task = create_task(Download._download_file(task_info, progress, sem, settings, cookie))
            tasks.append(task)
        await gather(*tasks)

    @staticmethod
    def download_files(items: list[dict], account_id: str, account_mark: str,
                       settings: Settings, cleaner: Cleaner, cookie: Cookie):
        '''下载作品文件'''
        print(f'[{Colors.CYAN}]\n开始下载作品文件\n')
        save_folder = Download._create_save_folder(account_id, account_mark, settings)
        tasks_info = Download._generate_task(items, save_folder, settings, cleaner)
        with Download._progress_object() as progress:
            run(Download._download_files(tasks_info, progress, settings, cookie))
