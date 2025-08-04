"""
@Author         : Ailitonia
@Date           : 2025/8/4 14:44:00
@FileName       : artwork.py
@Project        : omega-miya
@Description    : 图站及相关 API 数据
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from typing import Annotated, TypeAlias

from nonebot.params import Depends

from src.service import OmegaMatcherInterface as OmMI
from ..manager import MessageContextManager
from ...artwork_proxy.models import ArtworkData

ARTWORK_CONTEXT_MANAGER = MessageContextManager(data_type=ArtworkData)
"""作品信息上下文管理器"""
OPTIONAL_REPLY_ARTWORK_CONTEXT: TypeAlias = Annotated[
    tuple[OmMI, ArtworkData | None], Depends(ARTWORK_CONTEXT_MANAGER.get_reply_context, use_cache=True)
]
"""获取回复消息中作品信息的子依赖"""

__all__ = [
    'ARTWORK_CONTEXT_MANAGER',
    'OPTIONAL_REPLY_ARTWORK_CONTEXT',
]
