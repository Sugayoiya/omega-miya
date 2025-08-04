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
from pydantic import BaseModel, ConfigDict

from src.service import OmegaMatcherInterface as OmMI
from ..manager import MessageContextManager


class MinimalArtworkData(BaseModel):
    origin: str
    aid: str
    uid: str

    model_config = ConfigDict(extra='ignore', coerce_numbers_to_str=True, frozen=True)


class MinimalArtistData(BaseModel):
    origin: str
    uid: str

    model_config = ConfigDict(extra='ignore', coerce_numbers_to_str=True, frozen=True)


ARTWORK_CONTEXT_MANAGER = MessageContextManager(data_type=MinimalArtworkData)
"""作品信息上下文管理器"""
OPTIONAL_REPLY_ARTWORK_CONTEXT: TypeAlias = Annotated[
    tuple[OmMI, MinimalArtworkData | None],
    Depends(ARTWORK_CONTEXT_MANAGER.get_reply_context, use_cache=True)
]
"""获取回复消息中作品信息的子依赖"""

ARTIST_CONTEXT_MANAGER = MessageContextManager(data_type=MinimalArtistData)
"""作品用户信息上下文管理器"""
OPTIONAL_REPLY_ARTIST_CONTEXT: TypeAlias = Annotated[
    tuple[OmMI, MinimalArtistData | None],
    Depends(ARTIST_CONTEXT_MANAGER.get_reply_context, use_cache=True)
]
"""获取回复消息中作品用户信息的子依赖"""


__all__ = [
    'ARTIST_CONTEXT_MANAGER',
    'ARTWORK_CONTEXT_MANAGER',
    'OPTIONAL_REPLY_ARTIST_CONTEXT',
    'OPTIONAL_REPLY_ARTWORK_CONTEXT',
]
