"""
@Author         : Ailitonia
@Date           : 2025/8/8 10:13:02
@FileName       : depends.py
@Project        : omega-miya
@Description    : 通用子依赖
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from typing import Annotated

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Event as BaseEvent
from nonebot.params import Depends

from src.service import OmegaMatcherInterface as OmMI

type OMEGA_MATCHER_INTERFACE = Annotated[OmMI, Depends(OmMI.depend())]
"""子依赖: OmegaMatcherInterface"""


def _event_user_nickname(bot: BaseBot, event: BaseEvent) -> str:
    """获取当前事件用户昵称"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_user_nickname()


type EVENT_USER_NICKNAME = Annotated[str, Depends(_event_user_nickname, use_cache=True)]
"""子依赖: 获取当前事件用户昵称"""


def _event_msg_mentioned_user_ids(bot: BaseBot, event: BaseEvent) -> list[str]:
    """获取当前事件消息中被 @ 所有用户对象 ID 列表"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_msg_mentioned_user_ids()


type EVENT_MSG_MENTIONED_USER_IDS = Annotated[list[str], Depends(_event_msg_mentioned_user_ids, use_cache=True)]
"""子依赖: 获取当前事件消息中被 @ 所有用户对象 ID 列表"""


def _event_msg_image_urls(bot: BaseBot, event: BaseEvent) -> list[str]:
    """获取当前事件消息中的全部图片链接"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_msg_image_urls()


type EVENT_MSG_IMAGE_URLS = Annotated[list[str], Depends(_event_msg_image_urls, use_cache=True)]
"""子依赖: 获取当前事件消息中的全部图片链接"""


def _event_reply_message_id(bot: BaseBot, event: BaseEvent) -> str | None:
    """获取事件回复或引用消息 ID"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_reply_msg_id()


type OPTIONAL_EVENT_REPLY_MESSAGE_ID = Annotated[str | None, Depends(_event_reply_message_id, use_cache=True)]
"""子依赖: 获取事件回复或引用消息 ID"""


def _event_reply_msg_image_urls(bot: BaseBot, event: BaseEvent) -> list[str]:
    """获取当前事件回复消息中的全部图片链接"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_reply_msg_image_urls()


type EVENT_REPLY_MSG_IMAGE_URLS = Annotated[list[str], Depends(_event_reply_msg_image_urls, use_cache=True)]
"""子依赖: 获取当前事件回复消息中的全部图片链接"""


def _event_reply_msg_plain_text(bot: BaseBot, event: BaseEvent) -> str | None:
    """获取当前事件回复消息的文本"""
    return OmMI.get_event_depend_type(target_event=event)(bot=bot, event=event).get_reply_msg_plain_text()


type OPTIONAL_EVENT_REPLY_MSG_PLAIN_TEXT = Annotated[str | None, Depends(_event_reply_msg_plain_text, use_cache=True)]
"""子依赖: 获取当前事件回复消息的文本"""

__all__ = [
    'EVENT_USER_NICKNAME',
    'EVENT_MSG_MENTIONED_USER_IDS',
    'EVENT_MSG_IMAGE_URLS',
    'OMEGA_MATCHER_INTERFACE',
    'OPTIONAL_EVENT_REPLY_MESSAGE_ID',
    'EVENT_REPLY_MSG_IMAGE_URLS',
    'OPTIONAL_EVENT_REPLY_MSG_PLAIN_TEXT',
]
