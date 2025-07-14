"""
@Author         : Ailitonia
@Date           : 2025/7/14 10:10:25
@FileName       : helpers.py
@Project        : omega-miya
@Description    : 工具类函数
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from http.cookiejar import CookieJar
from typing import TYPE_CHECKING, Generator

from multidict import CIMultiDict
from nonebot.internal.driver import Cookies as Cookies

if TYPE_CHECKING:
    from .types import CookieTypes, HeaderTypes


def iter_cookies_types_item(cookies: 'CookieTypes') -> Generator[tuple[str, str], None, None]:
    if cookies is None:
        return
    elif isinstance(cookies, Cookies):
        for item in cookies:
            yield item.name, item.value if item.value is not None else ''
    elif isinstance(cookies, CookieJar):
        for item in cookies:
            yield item.name, item.value if item.value is not None else ''
    elif isinstance(cookies, dict):
        for k, v in cookies.items():
            yield k, v if v is not None else ''
    elif isinstance(cookies, list):
        for item in cookies:
            yield item[0], item[1]
    else:
        raise TypeError(f'Unsupported cookies type: {type(cookies)}')


def iter_headers_types_item(headers: 'HeaderTypes') -> Generator[tuple[str, str], None, None]:
    if headers is None:
        return
    elif isinstance(headers, CIMultiDict):
        for k, v in headers.items():
            yield k, v if v is not None else ''
    elif isinstance(headers, dict):
        for k, v in headers.items():
            yield k, v if v is not None else ''
    elif isinstance(headers, list):
        for item in headers:
            yield item[0], item[1]
    else:
        raise TypeError(f'Unsupported headers type: {type(headers)}')


__all__ = [
    'iter_cookies_types_item',
    'iter_headers_types_item',
]
