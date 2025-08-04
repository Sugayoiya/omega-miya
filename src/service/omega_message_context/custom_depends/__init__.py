"""
@Author         : Ailitonia
@Date           : 2025/8/4 14:41:55
@FileName       : custom_depends.py
@Project        : omega-miya
@Description    : 自定义数据类子依赖
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from .artwork import ARTWORK_CONTEXT_MANAGER, OPTIONAL_REPLY_ARTWORK_CONTEXT

__all__ = [
    'ARTWORK_CONTEXT_MANAGER',
    'OPTIONAL_REPLY_ARTWORK_CONTEXT',
]
