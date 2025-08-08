"""
@Author         : Ailitonia
@Date           : 2025/8/8 10:13:02
@FileName       : depends.py
@Project        : omega-miya
@Description    : 通用子依赖
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from typing import Annotated, Any

from nonebot.adapters import Bot as BaseBot
from nonebot.adapters import Event as BaseEvent
from nonebot.adapters import Message as BaseMessage
from nonebot.params import Depends
from nonebot.typing import T_State

from src.service import OmegaMatcherInterface as OmMI

type EVENT_MATCHER_INTERFACE = Annotated[OmMI, Depends(OmMI.depend(acquire_type='event'))]
"""子依赖: 事件对象的 OmegaMatcherInterface"""

type USER_MATCHER_INTERFACE = Annotated[OmMI, Depends(OmMI.depend(acquire_type='user'))]
"""子依赖: 用户对象的 OmegaMatcherInterface"""


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


class StatePlainTextInner:
    """State 中的纯文本值"""

    def __init__(self, key: Any):
        self.key = key

    def __call__(self, state: T_State) -> str:
        value = state.get(self.key, None)
        if value is None:
            raise KeyError(f'State has not key: {self.key}')
        elif isinstance(value, str):
            return value
        elif isinstance(value, BaseMessage):
            return value.extract_plain_text()
        else:
            return str(value)


def state_plain_text(key: str) -> str:
    """子依赖: 获取 State 中的纯文本值"""
    return Depends(StatePlainTextInner(key=key), use_cache=True)


__all__ = [
    'EVENT_MSG_MENTIONED_USER_IDS',
    'EVENT_MSG_IMAGE_URLS',
    'EVENT_MATCHER_INTERFACE',
    'EVENT_REPLY_MSG_IMAGE_URLS',
    'EVENT_USER_NICKNAME',
    'OPTIONAL_EVENT_REPLY_MESSAGE_ID',
    'OPTIONAL_EVENT_REPLY_MSG_PLAIN_TEXT',
    'USER_MATCHER_INTERFACE',
    'state_plain_text',
]
