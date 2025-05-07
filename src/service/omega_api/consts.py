"""
@Author         : Ailitonia
@Date           : 2025/2/8 16:54:48
@FileName       : consts.py
@Project        : omega-miya
@Description    : Omega API 常量
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from typing import Literal

APP_HEADER_KEY: Literal['X-OmegaAPI-App'] = 'X-OmegaAPI-App'
"""Omega API 验证 APP 名称的 Header Key"""
TIMESTAMP_HEADER_KEY: Literal['X-OmegaAPI-Timestamp'] = 'X-OmegaAPI-Timestamp'
"""Omega API 验证时间戳的 Header Key"""
TOKEN_HEADER_KEY: Literal['X-OmegaAPI-Token'] = 'X-OmegaAPI-Token'
"""Omega API 身份验证 Token 的 Header Key"""


__all__ = [
    'APP_HEADER_KEY',
    'TIMESTAMP_HEADER_KEY',
    'TOKEN_HEADER_KEY',
]
