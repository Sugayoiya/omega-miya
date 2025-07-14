"""
@Author         : Ailitonia
@Date           : 2024/6/12 上午1:07
@FileName       : requests
@Project        : nonebot2_miya
@Description    : OmegaRequests, 通过对 ForwardDriver 的二次封装实现 HttpClient 功能
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

import hashlib
import pathlib
import re
from asyncio.exceptions import TimeoutError as AsyncTimeoutError
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import unquote, urlparse

import ujson
from nonebot import get_driver, logger
from nonebot.drivers import (
    ForwardDriver,
    HTTPClientMixin,
    Request,
    WebSocketClientMixin,
)

from src.exception import WebSourceException
from .config import http_proxy_config

if TYPE_CHECKING:
    from src.resource import BaseResource

    from .types import (
        ContentTypes,
        CookieTypes,
        DataTypes,
        FilesTypes,
        HTTPClientSession,
        HeaderTypes,
        QueryTypes,
        Response,
        WebSocket,
    )


class OmegaRequests:
    """对 ForwardDriver 二次封装实现的 HttpClient"""

    _default_retry_limit: int = 3
    _default_timeout_time: float = 10.0
    _default_headers: dict[str, str] = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'dnt': '1',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36'
    }

    def __init__(
            self,
            *,
            timeout: float | None = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            retry: int | None = None,
    ):
        self.driver = get_driver()
        if not isinstance(self.driver, ForwardDriver):
            raise RuntimeError(
                f"Current driver {self.driver.type} doesn't support forward connections! "
                "OmegaRequests need a ForwardDriver to work."
            )

        self.cookies = cookies
        self.cookies = None if not self.cookies else self.cookies
        self.headers = self._default_headers if headers is None else headers
        self.headers = None if not self.headers else self.headers
        self.retry_limit = self._default_retry_limit if retry is None else retry
        self.timeout = self._default_timeout_time if timeout is None else timeout

    @staticmethod
    def parse_content_as_bytes(response: 'Response', encoding: str = 'utf-8') -> bytes:
        """解析 Response Content 为 bytes"""
        if isinstance(response.content, str):
            return response.content.encode(encoding=encoding)
        elif isinstance(response.content, bytes):
            return response.content
        else:
            return b'' if response.content is None else bytes(response.content)

    @staticmethod
    def parse_content_as_json(response: 'Response', **kwargs) -> Any:
        """解析 Response Content 为 Json"""
        if response.content is None:
            raise ValueError('content of response is None')
        return ujson.loads(response.content, **kwargs)

    @staticmethod
    def parse_content_as_text(response: 'Response', encoding: str = 'utf-8') -> str:
        """解析 Response Content 为字符串"""
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, bytes):
            return response.content.decode(encoding=encoding)
        else:
            return '' if response.content is None else str(response.content)

    @classmethod
    async def iter_content_as_lines(
            cls,
            stream_requester: AsyncGenerator['Response', Any],
            *,
            encoding: str = 'utf-8',
    ) -> AsyncGenerator[str, None]:
        """解析流式请求, 按文本行迭代"""
        buffer: bytes = b''
        trailing_cr: bool = False

        async for response in stream_requester:
            content = cls.parse_content_as_bytes(response, encoding=encoding)

            # Always push a trailing `\r` into the next iteration.
            if trailing_cr:
                content = b'\r' + content
                trailing_cr = False
            if content.endswith(b'\r'):
                trailing_cr = True
                content = content[:-1]

            if not content:
                continue

            trailing_newline = content[-1] in [b'\r', b'\n']
            lines = content.splitlines()

            if len(lines) == 1 and not trailing_newline:
                # No new lines, buffer the input and continue.
                buffer += lines[0]
                continue

            if buffer:
                # Include any existing buffer in the first portion of the splitlines result.
                lines = [buffer + lines[0]] + lines[1:]
                buffer = b''

            if not trailing_newline:
                # If the last segment of splitlines is not newline terminated,
                # then drop it from our output and start a new buffer.
                buffer = lines.pop()

            for line in lines:
                yield line.decode(encoding=encoding)

        if not buffer and not trailing_cr:
            return

        yield buffer.decode(encoding=encoding)

    @classmethod
    def parse_url_file_name(cls, url: str) -> str:
        """尝试解析 url 对应的文件名"""
        parsed_url = urlparse(url=url, allow_fragments=True)
        original_file_name = pathlib.PurePath(unquote(parsed_url.path)).name
        return original_file_name

    @classmethod
    def hash_url_file_name(cls, *prefix: str, url: str) -> str:
        """尝试解析 url 对应的文件后缀名并用 hash 和前缀代替"""
        parsed_url = urlparse(url=url, allow_fragments=True)
        name_hash = hashlib.sha256(url.encode(encoding='utf8')).hexdigest()
        name_suffix = pathlib.PurePath(unquote(parsed_url.path)).suffix
        name_prefix = '_'.join(prefix) if prefix else 'file'
        new_name = f'{name_prefix}_{name_hash}{name_suffix}'
        return new_name

    @classmethod
    def get_url_in_text(cls, text: str) -> list[str]:
        """匹配并提取字符串中的合法 URL"""
        pattern = re.compile(r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^/\s]*)*')
        parsed_urls = [urlparse(str(x)) for x in re.findall(pattern, text)]
        return [
            x.geturl() for x in parsed_urls
            if all((x.scheme in ['http', 'https'], x.netloc))
        ]

    @classmethod
    def get_default_headers(cls) -> dict[str, str]:
        return deepcopy(cls._default_headers)

    def get_session(self, params: Optional['QueryTypes'] = None, use_proxy: bool = True) -> 'HTTPClientSession':
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.driver.type} doesn't support forward http connections! "
                "OmegaRequests need a HTTPClient Driver to work."
            )
        return self.driver.get_session(
            params=params,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )

    async def request(self, setup: Request) -> 'Response':
        """发送一个 HTTP 请求, 自动重试"""
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.driver.type} doesn't support forward http connections! "
                "OmegaRequests need a HTTPClient Driver to work."
            )

        # 处理自动重试
        attempts_num = 0
        final_exception = None
        while attempts_num < self.retry_limit:
            try:
                logger.opt(colors=True).trace(f'<lc>Omega Requests</lc> | Starting request <ly>{setup!r}</ly>')
                return await self.driver.request(setup=setup)
            except AsyncTimeoutError as e:
                logger.opt(colors=True).debug(
                    f'<lc>Omega Requests</lc> | <ly>{setup!r} failed on the {attempts_num + 1} attempt</ly> <c>></c> '
                    '<r>TimeoutError</r>'
                )
                final_exception = e
            except Exception as e:
                logger.opt(colors=True).warning(
                    f'<lc>Omega Requests</lc> | <ly>{setup!r} failed on the {attempts_num + 1} attempt</ly> <c>></c> '
                    f'<r>Exception {e.__class__.__name__}</r>: {e}'
                )
                final_exception = e
            finally:
                attempts_num += 1

        logger.opt(colors=True).error(
            f'<lc>Omega Requests</lc> | <ly>{setup!r} failed with {attempts_num} times attempts</ly> <c>></c> '
            '<r>ExceededAttemptLimited</r>: The number of attempts exceeds limit with final exception: '
            f'<r>{final_exception.__class__.__name__}</r>: {final_exception}'
        )
        raise WebSourceException(500, 'The number of attempts exceeds limit.') from final_exception

    async def stream_request(
            self,
            setup: Request,
            *,
            chunk_size: int = 1024,
    ) -> AsyncGenerator['Response', None]:
        """发送一个 HTTP 流式请求"""
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(
                f"Current driver {self.driver.type} doesn't support forward http connections! "
                "OmegaRequests need a HTTPClient Driver to work."
            )

        try:
            logger.opt(colors=True).trace(f'<lc>Omega Requests</lc> | Starting request <ly>{setup!r}</ly>')
            async for response in self.driver.stream_request(setup, chunk_size=chunk_size):
                yield response
        except AsyncTimeoutError as e:
            logger.opt(colors=True).debug(
                f'<lc>Omega Requests</lc> | <ly>{setup!r} failed</ly> with <r>TimeoutError</r>'
            )
            raise WebSourceException(504, 'Timeout') from e
        except Exception as e:
            logger.opt(colors=True).warning(
                f'<lc>Omega Requests</lc> | <ly>{setup!r} failed</ly>, <r>Exception {e.__class__.__name__}</r>: {e}'
            )
            raise WebSourceException(500, 'Timeout') from e

    @asynccontextmanager
    async def websocket(
            self,
            method: str,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
    ) -> AsyncGenerator['WebSocket', None]:
        """建立 websocket 连接"""
        if not isinstance(self.driver, WebSocketClientMixin):
            raise RuntimeError(
                f"Current driver {self.driver.type} doesn't support forward webSocket connections! "
                "OmegaRequests need a WebSocketClient Driver to work."
            )

        setup = Request(
            method=method,
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )

        async with self.driver.websocket(setup=setup) as ws:
            yield ws

    async def get(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
    ) -> 'Response':
        """发送一个 GET 请求"""
        setup = Request(
            method='GET',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        return await self.request(setup=setup)

    async def post(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
    ) -> 'Response':
        """发送一个 POST 请求"""
        setup = Request(
            method='POST',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        return await self.request(setup=setup)

    async def put(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
    ) -> 'Response':
        """发送一个 PUT 请求"""
        setup = Request(
            method='PUT',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        return await self.request(setup=setup)

    async def delete(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
    ) -> 'Response':
        """发送一个 DELETE 请求"""
        setup = Request(
            method='DELETE',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        return await self.request(setup=setup)

    async def stream_get(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
            chunk_size: int = 1024,
    ) -> AsyncGenerator['Response', None]:
        """发送一个 GET 流式请求"""
        setup = Request(
            method='GET',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        async for response in self.stream_request(setup, chunk_size=chunk_size):
            yield response

    async def stream_get_iter_lines(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
            chunk_size: int = 1024,
            encoding: str = 'utf-8',
    ) -> AsyncGenerator[str, None]:
        """发送一个 GET 流式请求, 按行迭代"""
        setup = Request(
            method='GET',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        async for line in self.iter_content_as_lines(
                stream_requester=self.stream_request(setup, chunk_size=chunk_size),
                encoding=encoding,
        ):
            yield line

    async def stream_post(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
            chunk_size: int = 1024,
    ) -> AsyncGenerator['Response', None]:
        """发送一个 POST 流式请求"""
        setup = Request(
            method='POST',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        async for response in self.stream_request(setup, chunk_size=chunk_size):
            yield response

    async def stream_post_iter_lines(
            self,
            url: str,
            *,
            params: 'QueryTypes' = None,
            headers: 'HeaderTypes' = None,
            cookies: 'CookieTypes' = None,
            content: 'ContentTypes' = None,
            data: 'DataTypes' = None,
            json: Any = None,
            files: 'FilesTypes' = None,
            timeout: float | None = None,
            use_proxy: bool = True,
            chunk_size: int = 1024,
            encoding: str = 'utf-8',
    ) -> AsyncGenerator[str, None]:
        """发送一个 POST 流式请求, 按行迭代"""
        setup = Request(
            method='POST',
            url=url,
            params=params,
            headers=self.headers if headers is None else headers,
            cookies=self.cookies if cookies is None else cookies,
            content=content,
            data=data,
            json=json,
            files=files,
            timeout=self.timeout if timeout is None else timeout,
            proxy=http_proxy_config.proxy_url if use_proxy else None
        )
        async for line in self.iter_content_as_lines(
                stream_requester=self.stream_request(setup, chunk_size=chunk_size),
                encoding=encoding,
        ):
            yield line

    async def download[T: 'BaseResource'](
            self,
            url: str,
            file: T,
            *,
            params: 'QueryTypes' = None,
            ignore_exist_file: bool = False,
            **kwargs,
    ) -> T:
        """下载文件

        :param url: 链接
        :param file: 下载目标路径
        :param params: 请求参数
        :param ignore_exist_file: 忽略已存在文件
        :return: 下载目标路径
        """
        if ignore_exist_file and file.is_file:
            logger.opt(colors=True).info(
                f'<lc>Omega Requests</lc> | Download <ly>{url}</ly> to {file} ignored by exist file'
            )
            return file

        logger.opt(colors=True).debug(
            f'<lc>Omega Requests</lc> | Starting download <ly>{url}</ly> to {file}'
        )

        response = await self.get(url=url, params=params, **kwargs)

        if response.status_code != 200:
            logger.opt(colors=True).error(
                f'<lc>Omega Requests</lc> | Download <ly>{url}</ly> to {file} '
                f'failed with code <lr>{response.status_code!r}</lr>'
            )
            raise WebSourceException(
                response.status_code,
                f'Download {url} to {file} failed with code {response.status_code!r}'
            )

        async with file.async_open(mode='wb') as af:
            await af.write(self.parse_content_as_bytes(response=response))

        logger.opt(colors=True).success(
            f'<lc>Omega Requests</lc> | Download <ly>{url}</ly> to {file} completed'
        )
        return file

    async def stream_download[T: 'BaseResource'](
            self,
            url: str,
            file: T,
            *,
            params: 'QueryTypes' = None,
            chunk_size: int = 1024 * 16,
            ignore_exist_file: bool = False,
            **kwargs,
    ) -> T:
        """流式下载文件, 支持断点续传

        :param url: 链接
        :param file: 下载目标路径
        :param params: 请求参数
        :param chunk_size: 分块大小, 默认 16 KB
        :param ignore_exist_file: 忽略已存在文件, 会同时忽略断点续传
        :return: 下载目标路径
        """
        if ignore_exist_file and file.is_file:
            logger.opt(colors=True).info(
                f'<lc>Omega Requests</lc> | Download <ly>{url}</ly> to {file} ignored by exist file'
            )
            return file

        clear_restart = False
        start_byte = file.file_size if file.is_file else 0
        headers = dict(self.headers if self.headers is not None else {})
        if start_byte > 0:
            headers.update({'Range': f'bytes={start_byte}-'})

        logger.opt(colors=True).debug(
            f'<lc>Omega Requests</lc> | Starting stream download <ly>{url}</ly> to {file}'
        )

        # 追加写入模式打开文件, 分块写入
        async with file.async_open(mode='ab') as af:
            async for response in self.stream_get(
                    url=url, params=params, headers=headers, chunk_size=chunk_size, **kwargs
            ):
                if start_byte > 0 and response.status_code == 206:
                    pass
                elif start_byte > 0 and response.status_code != 206:
                    logger.opt(colors=True).warning(
                        f'<lc>Omega Requests</lc> | Stream download <ly>{url}</ly> to {file} failed, '
                        'the server does not support breakpoint resuming, and will re-download'
                    )
                    clear_restart = True
                    break
                elif response.status_code != 200:
                    logger.opt(colors=True).error(
                        f'<lc>Omega Requests</lc> | Stream download <ly>{url}</ly> to {file} '
                        f'failed with code <lr>{response.status_code!r}</lr>'
                    )
                    raise WebSourceException(
                        response.status_code,
                        f'Download {url} to {file} failed with code {response.status_code!r}'
                    )

                await af.write(self.parse_content_as_bytes(response=response))

        # 如果需要重新下载, 清空文件并重新请求
        if clear_restart:
            async with file.async_open(mode='wb') as _:
                pass
            return await self.stream_download(
                url, file, params=params, chunk_size=chunk_size, ignore_exist_file=ignore_exist_file, **kwargs
            )

        logger.opt(colors=True).success(
            f'<lc>Omega Requests</lc> | Download <ly>{url}</ly> to {file} completed'
        )
        return file


__all__ = [
    'OmegaRequests',
]
