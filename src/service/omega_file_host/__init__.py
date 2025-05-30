"""
@Author         : Ailitonia
@Date           : 2025/5/30 11:11:36
@FileName       : omega_file_host.py
@Project        : omega-miya
@Description    : 文件托管服务, 通过 HTTP API 提供文件内容
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from .api import get_hosting_file_path

__all__ = [
    'get_hosting_file_path',
]
