from pathlib import Path, PosixPath
import datetime

from douyin_download.config.settings import Settings, Account
from douyin_download.models import AccountRoutine, DownloadInfo
from douyin_download.parser.models import ItemInfo
from douyin_download.parser import generate_download_info_list


def test_generate_download_info_list():
    account_info = AccountRoutine(
        id="1736848482507527", name="原神", mark="fake_mark  fwa*?81"
    )
    item_info_list = (
        ItemInfo(
            id="7637507783696387355",
            desc="#原神 《原神》至冬前瞻短片 - 风雪翳蔽的冻土",
            create_timestamp=1778245911,
            create_time=datetime.date(2026, 5, 8),
            type="video",
            share_url="https://www.douyin.com/video/7637507783696387355",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/7f8640c2f7cc70506c016ff13828b829/6a1ba841/video/tos/cn/tos-cn-ve-15/ogpfDwv4EmvaB6XAIjJ9ZAA8Q9i46Df3og2BAi/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2239&bt=2239&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=ZTczNGc1ZTs6NWk6Nmg7O0BpM2l1d2o5cmt4OjMzNGkzM0A1XzEyMzMxXi4xNDRjYmMzYSNhaXJfMmRzLXJhLS1kLTBzcw%3D%3D&btag=c0000e00018000&cquery=100o_101r_100B_100H_100K&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1920,
            height=1080,
            index=None,
            data_size=10060063,
        ),
        ItemInfo(
            id="7595785227641834798",
            desc="地方传奇——「黑枪太婆」海捷德 #原神空月之歌 #原神月之四新区域",
            create_timestamp=1768557601,
            create_time=datetime.date(2026, 1, 16),
            type="video",
            share_url="https://www.douyin.com/video/7595785227641834798",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/30fac8549789aa6701cc8847ed8b7a15/6a1ba837/video/tos/cn/tos-cn-ve-15/oI8hiQD5iIUGLgqQIPAB9maWmAE2vQCvGIslW/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2709&bt=2709&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=ZjxmaTdkNTg8PDg0OGQ5ZEBpM2k4PHc5cjl0ODMzNGkzM0A1Y2MzLi82XzAxLTE2Xi5fYSMuYWhyMmRrXmhhLS1kLS9zcw%3D%3D&btag=c0000e00010000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=0ea98fd3bdc3c6c14a3d0804cc272721&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1080,
            height=1920,
            index=None,
            data_size=8730817,
        ),
        ItemInfo(
            id="7549035681759120682",
            desc="😏 #原神空月之歌 #原神挪德卡莱",
            create_timestamp=1757660400,
            create_time=datetime.date(2025, 9, 12),
            type="video",
            share_url="https://www.douyin.com/video/7549035681759120682",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/a1360e98b3bfbed88847a1d20b6eac54/6a1ba831/video/tos/cn/tos-cn-ve-15/oMPHgeYTGBORLHRBPHIjxcQMhCGIy4fAYK7f7A/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=3256&bt=3256&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=N2g3NDg0NjVmaTQ5Zjo1OkBpM2ZrPHA5cnNyNjMzNGkzM0BgYjRiLzAyX2AxMy5eLjAzYSNiczMzMmRzci5hLS1kLTBzcw%3D%3D&btag=c0000e00010000&cquery=100B_100H_100K_100o_101r&dy_q=1780186606&feature_id=0ea98fd3bdc3c6c14a3d0804cc272721&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1080,
            height=1920,
            index=None,
            data_size=7922856,
        ),
        ItemInfo(
            id="7645248723966053668",
            desc="#原神 《原神》过场动画-「因果熔炉」",
            create_timestamp=1780135200,
            create_time=datetime.date(2026, 5, 30),
            type="video",
            share_url="https://www.douyin.com/video/7645248723966053668",
            format=".dash",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/c12d725a27301674a171032c18f31bf1/6a1ba860/video/tos/cn/tos-cn-ve-15/okNB7WxiiYVQEPigq7AAruVfxe59BRAGaIAt9X/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2767&bt=2767&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aDk8PGY6NGhoZzc1aWY1N0BpajNneXM5cjtvOzMzNGkzM0BgXy1eMGEtNTMxLjMyLl8uYSNxYmFsMmRzcmBhLS1kLWFzcw%3D%3D&btag=c0000e00028000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1920,
            height=1080,
            index=None,
            data_size=23631916,
        ),
        ItemInfo(
            id="7645532646574968100",
            desc="自然。",
            create_timestamp=1780114293,
            create_time=datetime.date(2026, 5, 30),
            type="video",
            share_url="https://www.douyin.com/video/7645532646574968100",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/db0b8591e016cded3b6ef348dccc686e/6a1ba829/video/tos/cn/tos-cn-ve-15/oYIQvbDEwTui4gp6PZxCh8a3iBqpaxAlBIFQA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=1429&bt=1429&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aGU7aGk6ZmY6ZDQ8PDNmZkBpanVwdnQ5cjU5OzMzNGkzM0BiX18vNGJeNTUxYl9hM181YSNvZjUuMmRrLWFhLS1kLTBzcw%3D%3D&btag=c0000e00008000&cquery=100H_100K_100o_101r_100B&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1080,
            height=1920,
            index=None,
            data_size=2046052,
        ),
        ItemInfo(
            id="7645245241552817444",
            desc="#原神 《原神》过场动画-「虚世净火」",
            create_timestamp=1780113600,
            create_time=datetime.date(2026, 5, 30),
            type="video",
            share_url="https://www.douyin.com/video/7645245241552817444",
            format=".dash",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/e96f7ed548e0b8c614ffd2a41b59d8d2/6a1ba85f/video/tos/cn/tos-cn-ve-15/oQU5QfO8DAMqFi4AxbELVMIzGBCE3Lmgeb9JzA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2560&bt=2560&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWY5O2hnZjQzNTw0ZWk3M0Bpamg1eXg5cnZvOzMzNGkzM0A2Ml40MTIvXzQxYDYxL2BiYSMyYDRvMmRjbWBhLS1kLS9zcw%3D%3D&btag=c0000e00028000&cquery=100o_101r_100B_100H_100K&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1920,
            height=1080,
            index=None,
            data_size=21532440,
        ),
        ItemInfo(
            id="7645161267329617206",
            desc="这一篇故事已然落笔，下一篇故事未完待续。#原神空月之歌",
            create_timestamp=1780027824,
            create_time=datetime.date(2026, 5, 29),
            type="video",
            share_url="https://www.douyin.com/video/7645161267329617206",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/c520f9fe7fb82d6796a027d83f4d18fe/6a1ba828/video/tos/cn/tos-cn-ve-15/oM2weCfPAj5IKgGo8fMFEuFYQEAfXCPyMADKDY/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=1130&bt=1130&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=Mzg1Mzs7NzUzPGRoZDtnZUBpMzh4M2s5cnFpOzMzNGkzM0AuM18vYy42NmExLzUzMl4wYSNjMi1qMmRzb2BhLS1kLTBzcw%3D%3D&btag=c0000e00008000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1080,
            height=1920,
            index=None,
            data_size=1521798,
        ),
        ItemInfo(
            id="7645158977206029631",
            desc="#原神 《原神》过场动画-「三千明光」",
            create_timestamp=1780027291,
            create_time=datetime.date(2026, 5, 29),
            type="video",
            share_url="https://www.douyin.com/video/7645158977206029631",
            format=".dash",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/bd3e674d93eae950ec4193f57413946d/6a1ba8c5/video/tos/cn/tos-cn-ve-15/ogyCpxoIyUxGfEeKA50RfeIuLDA2YiYmRYK2JQ/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=3362&bt=3362&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWU4OjNlZ2dkM2k2aDw3aUBpM3J2c3M5cmlpOzMzNGkzM0BeLTMyMC0xXmIxYi0tNGAxYSNqXjZqMmQ0cGBhLS1kLWFzcw%3D%3D&btag=c0000e00028000&cquery=100K_100o_101r_100B_100H&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1920,
            height=1080,
            index=None,
            data_size=72167093,
        ),
        ItemInfo(
            id="7644790499647261990",
            desc="《原神》「月之七」版本创作者激励计划已开启，旅行者可前往【原神官号—专区】参与 #原神 #原神创作者激励计划 #原神空月之歌",
            create_timestamp=1779941498,
            create_time=datetime.date(2026, 5, 28),
            type="video",
            share_url="https://www.douyin.com/video/7644790499647261990",
            format=".mp4",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/2d9194099458efc572568b912b791cf5/6a1ba827/video/tos/cn/tos-cn-ve-15/o0BH7i2QAEwFeixABNufMgysr0CVB9gzXqI8AA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2654&bt=2654&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWRkOmgzOjVpO2hpZTc5OUBpajQ2a3A5cml2OzMzNGkzM0A2YmJiNS8yNmAxNTYuXjQvYSNeNXBtMmRjLV9hLS1kLWFzcw%3D%3D&btag=c0000e00008000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1080,
            height=1920,
            index=None,
            data_size=3066985,
        ),
        ItemInfo(
            id="7644789064909999406",
            desc="#原神 《原神》过场动画-「异栖之木」",
            create_timestamp=1779941162,
            create_time=datetime.date(2026, 5, 28),
            type="video",
            share_url="https://www.douyin.com/video/7644789064909999406",
            format=".dash",
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/93f079216bd2bce9b99997decedc9d28/6a1ba8b1/video/tos/cn/tos-cn-ve-15/oUnDPXKIvfIeXk7oAmQE2weL8ek0RuDMCG9EAR/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2015&bt=2015&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=NjhnPDs8NDo8Nzk2ODRmaEBpang5dXM5cmV1OzMzNGkzM0AwLWAxYWBhNmAxNDQ2NDBeYSNyZWxwMmRzbV9hLS1kLTBzcw%3D%3D&btag=c0000e00028000&cquery=100K_100o_101r_100B_100H&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            width=1920,
            height=1080,
            index=None,
            data_size=38004018,
        ),
    )
    download_info_list = (
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/7f8640c2f7cc70506c016ff13828b829/6a1ba841/video/tos/cn/tos-cn-ve-15/ogpfDwv4EmvaB6XAIjJ9ZAA8Q9i46Df3og2BAi/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2239&bt=2239&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=ZTczNGc1ZTs6NWk6Nmg7O0BpM2l1d2o5cmt4OjMzNGkzM0A1XzEyMzMxXi4xNDRjYmMzYSNhaXJfMmRzLXJhLS1kLTBzcw%3D%3D&btag=c0000e00018000&cquery=100o_101r_100B_100H_100K&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-08-7637507783696387355-video-#原神 《原神》至冬前瞻短片 - 风雪翳蔽的冻土 - fake_mark  fwa*?81.mp4"
            ),
            width=1920,
            height=1080,
            data_size=10060063,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/30fac8549789aa6701cc8847ed8b7a15/6a1ba837/video/tos/cn/tos-cn-ve-15/oI8hiQD5iIUGLgqQIPAB9maWmAE2vQCvGIslW/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2709&bt=2709&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=ZjxmaTdkNTg8PDg0OGQ5ZEBpM2k4PHc5cjl0ODMzNGkzM0A1Y2MzLi82XzAxLTE2Xi5fYSMuYWhyMmRrXmhhLS1kLS9zcw%3D%3D&btag=c0000e00010000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=0ea98fd3bdc3c6c14a3d0804cc272721&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-01-16-7595785227641834798-video-地方传奇——「黑枪太婆」海捷德 #原神空月之歌 #原神月之四新区域 - fake_mark  fwa*?81.mp4"
            ),
            width=1080,
            height=1920,
            data_size=8730817,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/a1360e98b3bfbed88847a1d20b6eac54/6a1ba831/video/tos/cn/tos-cn-ve-15/oMPHgeYTGBORLHRBPHIjxcQMhCGIy4fAYK7f7A/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=3256&bt=3256&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=N2g3NDg0NjVmaTQ5Zjo1OkBpM2ZrPHA5cnNyNjMzNGkzM0BgYjRiLzAyX2AxMy5eLjAzYSNiczMzMmRzci5hLS1kLTBzcw%3D%3D&btag=c0000e00010000&cquery=100B_100H_100K_100o_101r&dy_q=1780186606&feature_id=0ea98fd3bdc3c6c14a3d0804cc272721&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2025-09-12-7549035681759120682-video-😏 #原神空月之歌 #原神挪德卡莱 - fake_mark  fwa*?81.mp4"
            ),
            width=1080,
            height=1920,
            data_size=7922856,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/c12d725a27301674a171032c18f31bf1/6a1ba860/video/tos/cn/tos-cn-ve-15/okNB7WxiiYVQEPigq7AAruVfxe59BRAGaIAt9X/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2767&bt=2767&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aDk8PGY6NGhoZzc1aWY1N0BpajNneXM5cjtvOzMzNGkzM0BgXy1eMGEtNTMxLjMyLl8uYSNxYmFsMmRzcmBhLS1kLWFzcw%3D%3D&btag=c0000e00028000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-30-7645248723966053668-video-#原神 《原神》过场动画-「因果熔炉」 - fake_mark  fwa*?81.mp4"
            ),
            width=1920,
            height=1080,
            data_size=23631916,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/db0b8591e016cded3b6ef348dccc686e/6a1ba829/video/tos/cn/tos-cn-ve-15/oYIQvbDEwTui4gp6PZxCh8a3iBqpaxAlBIFQA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=1429&bt=1429&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aGU7aGk6ZmY6ZDQ8PDNmZkBpanVwdnQ5cjU5OzMzNGkzM0BiX18vNGJeNTUxYl9hM181YSNvZjUuMmRrLWFhLS1kLTBzcw%3D%3D&btag=c0000e00008000&cquery=100H_100K_100o_101r_100B&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-30-7645532646574968100-video-自然。 - fake_mark  fwa*?81.mp4"
            ),
            width=1080,
            height=1920,
            data_size=2046052,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/e96f7ed548e0b8c614ffd2a41b59d8d2/6a1ba85f/video/tos/cn/tos-cn-ve-15/oQU5QfO8DAMqFi4AxbELVMIzGBCE3Lmgeb9JzA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2560&bt=2560&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWY5O2hnZjQzNTw0ZWk3M0Bpamg1eXg5cnZvOzMzNGkzM0A2Ml40MTIvXzQxYDYxL2BiYSMyYDRvMmRjbWBhLS1kLS9zcw%3D%3D&btag=c0000e00028000&cquery=100o_101r_100B_100H_100K&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-30-7645245241552817444-video-#原神 《原神》过场动画-「虚世净火」 - fake_mark  fwa*?81.mp4"
            ),
            width=1920,
            height=1080,
            data_size=21532440,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/c520f9fe7fb82d6796a027d83f4d18fe/6a1ba828/video/tos/cn/tos-cn-ve-15/oM2weCfPAj5IKgGo8fMFEuFYQEAfXCPyMADKDY/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=1130&bt=1130&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=Mzg1Mzs7NzUzPGRoZDtnZUBpMzh4M2s5cnFpOzMzNGkzM0AuM18vYy42NmExLzUzMl4wYSNjMi1qMmRzb2BhLS1kLTBzcw%3D%3D&btag=c0000e00008000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-29-7645161267329617206-video-这一篇故事已然落笔，下一篇故事未完待续。#原神空月之歌 - fake_mark  fwa*?81.mp4"
            ),
            width=1080,
            height=1920,
            data_size=1521798,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/bd3e674d93eae950ec4193f57413946d/6a1ba8c5/video/tos/cn/tos-cn-ve-15/ogyCpxoIyUxGfEeKA50RfeIuLDA2YiYmRYK2JQ/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=3362&bt=3362&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWU4OjNlZ2dkM2k2aDw3aUBpM3J2c3M5cmlpOzMzNGkzM0BeLTMyMC0xXmIxYi0tNGAxYSNqXjZqMmQ0cGBhLS1kLWFzcw%3D%3D&btag=c0000e00028000&cquery=100K_100o_101r_100B_100H&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-29-7645158977206029631-video-#原神 《原神》过场动画-「三千明光」 - fake_mark  fwa*?81.mp4"
            ),
            width=1920,
            height=1080,
            data_size=72167093,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/2d9194099458efc572568b912b791cf5/6a1ba827/video/tos/cn/tos-cn-ve-15/o0BH7i2QAEwFeixABNufMgysr0CVB9gzXqI8AA/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2654&bt=2654&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=aWRkOmgzOjVpO2hpZTc5OUBpajQ2a3A5cml2OzMzNGkzM0A2YmJiNS8yNmAxNTYuXjQvYSNeNXBtMmRjLV9hLS1kLWFzcw%3D%3D&btag=c0000e00008000&cquery=101r_100B_100H_100K_100o&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-28-7644790499647261990-video-《原神》「月之七」版本创作者激励计划已开启，旅行者可前往【原神官号—专区】参与 #原神 #原神创作者激励计划 #原神空月之歌 - fake_mark  fwa*?81.mp4"
            ),
            width=1080,
            height=1920,
            data_size=3066985,
        ),
        DownloadInfo(
            url="https://v95-hzyy-thr-daily-web.douyinvod.com/93f079216bd2bce9b99997decedc9d28/6a1ba8b1/video/tos/cn/tos-cn-ve-15/oUnDPXKIvfIeXk7oAmQE2weL8ek0RuDMCG9EAR/?a=6383&ch=10010&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&cv=1&br=2015&bt=2015&cs=0&ds=4&ft=piBgHyfWzuuD.5XONgjNvjp~fytLjrKGo0TuRkaCfuQYljVhWL6&mime_type=video_mp4&qs=0&rc=NjhnPDs8NDo8Nzk2ODRmaEBpang5dXM5cmV1OzMzNGkzM0AwLWAxYWBhNmAxNDQ2NDBeYSNyZWxwMmRzbV9hLS1kLTBzcw%3D%3D&btag=c0000e00028000&cquery=100K_100o_101r_100B_100H&dy_q=1780186606&feature_id=37f92ebd2877ae8e7eba995d406c5150&l=20260531081646E2D9C87F8CE035B2BD41",
            path=PosixPath(
                "/tmp/sub/2026-05-28-7644789064909999406-video-#原神 《原神》过场动画-「异栖之木」 - fake_mark  fwa*?81.mp4"
            ),
            width=1920,
            height=1080,
            data_size=38004018,
        ),
    )

    _, settings = (
        (
            Account(
                mark="fake_mark /fwa*?81",
                url="https://www.douyin.com/user/fake_mark?fwa*?81",
                earliest="",
                latest="",
            ),
        ),
        Settings(
            save_folder=PosixPath("/tmp"),
            download_videos=True,
            download_images=True,
            download_horizontal_video=True,
            download_vertical_video=True,
            name_format=("create_time", "id", "type", "desc"),
            split="-",
            date_format="%Y-%m-%d",
            add_account_mark_to_end_of_name=True,
            file_description_max_length=64,
            timeout=300,
            concurrency=5,
            illegal_char={"\r", "/", "\t", "\x0b", "\x0c", "\x00", "\n"},
        ),
    )

    for index, download_info in enumerate(
        generate_download_info_list(
            account_info.mark, item_info_list, Path("/tmp/sub"), settings
        )
    ):
        assert download_info == download_info_list[index]
