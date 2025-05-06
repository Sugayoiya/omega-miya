"""
@Author         : Ailitonia
@Date           : 2025/2/9 14:16
@FileName       : api
@Project        : omega-miya
@Description    : Omega API
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

import hmac
import time
from collections.abc import Callable, Coroutine, Mapping
from hashlib import sha256
from inspect import iscoroutinefunction
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from nonebot import get_app, get_driver
from nonebot.log import logger
from nonebot.utils import run_sync

from src.compat import dump_json_as
from .config import api_config
from .consts import APP_HEADER_KEY, TIMESTAMP_HEADER_KEY, TOKEN_HEADER_KEY

_REGISTERED_APP: set[str] = set()
"""缓存全局已注册 app_name"""


class OmegaAPI:
    """Omega API 应用创建与路由注册"""

    def __init__(self, app_name: str, *, enable_token_verify: bool = False) -> None:
        self._enable_token_verify = enable_token_verify
        self._app_name = app_name.strip().removeprefix('/').removesuffix('/').strip()
        self._api_key = api_config.omega_api_key.get_secret_value()
        self._app = self._init_sub_app()
        self._root_url = self._get_root_url()

    @property
    def color_log_prefix(self) -> str:
        return f'<lc>Omega API</lc> | Service <lc>{self._app_name}</lc>'

    def _get_root_url(self) -> str:
        nonebot_confid = get_driver().config
        host = str(nonebot_confid.host)
        port = nonebot_confid.port
        if host in ['0.0.0.0', '127.0.0.1']:
            host = 'localhost'
        return f'http://{host}:{port}/{self._app_name}'

    @staticmethod
    def sign_params_hmac(key: str, app_name: str, params: Mapping[str, str]) -> str:
        """对请求参数进行签名

        请求 Headers 中应当包括:
          - X-OmegaAPI-App: 请求的 App 名称
          - X-OmegaAPI-Timestamp: 发起请求时的时间戳
          - X-OmegaAPI-Token: 计算出的签名 Token

        :return: 计算出的签名 Token 内容
        """
        timestamp = int(time.time())
        sorted_params = dict(sorted(params.items(), key=lambda x: (x[1], x[0])))
        sign_message = f'{app_name}.{timestamp}.{dump_json_as(dict[str, str], sorted_params)}'
        hmac_obj = hmac.new(key.encode(), sign_message.encode(), sha256)
        return hmac_obj.hexdigest()

    def verify_params_hmac(self, signature: str, timestamp: int | str, params: Mapping[str, str]) -> bool:
        """对请求参数签名进行校验"""
        sorted_params = dict(sorted(params.items(), key=lambda x: (x[1], x[0])))
        sign_message = f'{self._app_name}.{timestamp}.{dump_json_as(dict[str, str], sorted_params)}'
        hmac_obj = hmac.new(self._api_key.encode(), sign_message.encode(), sha256)
        return hmac.compare_digest(hmac_obj.hexdigest(), signature)

    @run_sync
    def async_verify_params_hmac(self, signature: str, timestamp: int | str, params: Mapping[str, Any]) -> bool:
        """对请求参数签名进行校验"""
        return self.verify_params_hmac(signature, timestamp, params)

    def _init_sub_app(self) -> FastAPI:
        """初始化子应用"""
        # 检查 nonebot 驱动器类型
        if 'fastapi' not in get_driver().type:
            raise RuntimeError('fastapi driver not enabled')

        # 检查 app_name 是否已被注册
        if self._app_name in _REGISTERED_APP:
            raise ValueError(f'OmegaAPI service {self._app_name!r} already registered')
        _REGISTERED_APP.add(self._app_name)

        # 创建子应用
        sub_app = FastAPI()

        # 配置 Token 校验中间件
        @sub_app.middleware('http')
        async def token_verify_middleware(request: Request, call_next):
            """参数签名校验中间件"""
            if not self._enable_token_verify:
                return await call_next(request)

            # 请求 App 名称校验
            request_app = request.headers.get(APP_HEADER_KEY, None)
            if request_app is None or request_app != self._app_name:
                return PlainTextResponse('Invalid Request App', status_code=403)

            # 请求时间戳校验
            request_timestamp = request.headers.get(TIMESTAMP_HEADER_KEY, None)
            if request_timestamp is None:
                return PlainTextResponse('Timestamp Not Provided', status_code=403)
            # 验证时间戳是否在合理范围内(±60秒)
            if not request_timestamp.isdigit() or abs(int(time.time()) - int(request_timestamp)) > 60:
                return PlainTextResponse('Invalid Timestamp', status_code=403)

            # 请求签名校验
            token = request.headers.get(TOKEN_HEADER_KEY, None)
            if token is None:
                return PlainTextResponse('Token Not Provided', status_code=403)

            if not await self.async_verify_params_hmac(token, request_timestamp, request.query_params):
                return PlainTextResponse('Invalid Token', status_code=403)

            return await call_next(request)

        # 挂载子应用
        nonebot_app: FastAPI = get_app()
        nonebot_app.mount(f'/{self._app_name}', sub_app)
        return sub_app

    def register_get_route(self, path: str):
        """包装 async function 并注册为 GET 路由

        :param path: 请求路径
        """
        path = f'/{path.strip().removeprefix("/").removesuffix("/").strip()}'

        def decorator[**P, T1, T2, R](func: Callable[P, Coroutine[T1, T2, R]]) -> Callable[P, Coroutine[T1, T2, R]]:
            if not iscoroutinefunction(func):
                raise ValueError('The decorated function must be coroutine function')

            self._app.get(path)(func)
            logger.opt(colors=True).info(
                f'{self.color_log_prefix} running at: (<lg>GET</lg>) <b><u>{self._root_url}{path}</u></b>'
            )
            return func

        return decorator

    def register_post_route(self, path: str):
        """包装 async function 并注册为 POST 路由

        :param path: 请求路径
        """
        path = f'/{path.strip().removeprefix("/").removesuffix("/").strip()}'

        def decorator[**P, T1, T2, R](func: Callable[P, Coroutine[T1, T2, R]]) -> Callable[P, Coroutine[T1, T2, R]]:
            if not iscoroutinefunction(func):
                raise ValueError('The decorated function must be coroutine function')

            self._app.post(path)(func)
            logger.opt(colors=True).info(
                f'{self.color_log_prefix} running at: (<ly>POST</ly>) <b><u>{self._root_url}{path}</u></b>'
            )
            return func

        return decorator

    def register_put_route(self, path: str):
        """包装 async function 并注册为 PUT 路由

        :param path: 请求路径
        """
        path = f'/{path.strip().removeprefix("/").removesuffix("/").strip()}'

        def decorator[**P, T1, T2, R](func: Callable[P, Coroutine[T1, T2, R]]) -> Callable[P, Coroutine[T1, T2, R]]:
            if not iscoroutinefunction(func):
                raise ValueError('The decorated function must be coroutine function')

            self._app.put(path)(func)
            logger.opt(colors=True).info(
                f'{self.color_log_prefix} running at: (<lc>PUT</lc>) <b><u>{self._root_url}{path}</u></b>'
            )
            return func

        return decorator

    def register_delete_route(self, path: str):
        """包装 async function 并注册为 DELETE 路由

        :param path: 请求路径
        """
        path = f'/{path.strip().removeprefix("/").removesuffix("/").strip()}'

        def decorator[**P, T1, T2, R](func: Callable[P, Coroutine[T1, T2, R]]) -> Callable[P, Coroutine[T1, T2, R]]:
            if not iscoroutinefunction(func):
                raise ValueError('The decorated function must be coroutine function')

            self._app.delete(path)(func)
            logger.opt(colors=True).info(
                f'{self.color_log_prefix} running at: (<lr>DELETE</lr>) <b><u>{self._root_url}{path}</u></b>'
            )
            return func

        return decorator


__all__ = [
    'OmegaAPI',
]
