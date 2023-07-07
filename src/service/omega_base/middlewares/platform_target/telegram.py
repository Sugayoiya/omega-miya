"""
@Author         : Ailitonia
@Date           : 2023/6/10 4:19
@FileName       : telegram
@Project        : nonebot2_miya
@Description    : Telegram 协议适配
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from pathlib import Path
from typing import Any, Iterable, Tuple, Type, Union, Optional, cast
from urllib.parse import urlparse, quote

from nonebot.adapters.telegram import (
    Bot as TelegramBot,
    Message as TelegramMessage,
    MessageSegment as TelegramMessageSegment,
    Event as TelegramEvent
)
from nonebot.adapters.telegram.event import (
    MessageEvent as TelegramMessageEvent,
    GroupMessageEvent as TelegramGroupMessageEvent,
    PrivateMessageEvent as TelegramPrivateMessageEvent,
    ChannelPostEvent as TelegramChannelPostEvent
)
from nonebot.adapters.telegram.message import Entity, File

from ..api_tools import register_api_caller
from ..const import SupportedPlatform, SupportedTarget
from ..entity_tools import register_entity_depend
from ..event_tools import register_event_handler
from ..message_tools import register_builder, register_extractor, register_sender
from ..types import (
    ApiCaller,
    EntityDepend,
    EntityParams,
    EventHandler,
    MessageBuilder,
    MessageExtractor,
    MessageSender,
    SenderParams,
    RevokeParams
)
from ...internal import OmegaEntity
from ...message import (
    MessageSegmentType,
    Message as OmegaMessage,
    MessageSegment as OmegaMessageSegment
)


@register_api_caller(adapter_name=SupportedPlatform.telegram.value)
class TelegramApiCaller(ApiCaller):
    """Telegram API 调用适配"""

    async def get_name(self, entity: OmegaEntity, id_: Optional[Union[int, str]] = None) -> str:
        chat_id = id_ if id_ is not None else entity.entity_id
        chat_data = await self.bot.call_api('get_chat', chat_id=chat_id)

        title = chat_data.title
        first_name = chat_data.first_name

        return title if title is not None else first_name if first_name is not None else ''

    async def get_profile_photo_url(self, entity: OmegaEntity, id_: Optional[Union[int, str]] = None) -> str:
        chat_id = id_ if id_ is not None else entity.entity_id
        chat_data = await self.bot.call_api('get_chat', chat_id=chat_id)

        if (photo := chat_data.photo) is None:
            raise RuntimeError('chat has no photo')

        file = await self.bot.call_api('get_file', file_id=photo.big_file_id)
        return f"https://api.telegram.org/file/bot{quote(self.bot.bot_config.token)}/{quote(file.file_path)}"


@register_builder(adapter_name=SupportedPlatform.telegram.value)
class TelegramMessageBuilder(MessageBuilder):

    @staticmethod
    def _construct(message: OmegaMessage) -> Iterable[TelegramMessageSegment]:

        def _iter_message(msg: OmegaMessage) -> Iterable[Tuple[str, dict]]:
            for seg in msg:
                yield seg.type, seg.data

        for type_, data in _iter_message(message):
            match type_:
                case MessageSegmentType.at.value:
                    yield Entity.mention(text='@' + data.get('user_id'))
                case MessageSegmentType.image.value:
                    url = data.get('url')
                    if urlparse(url).scheme not in ['http', 'https']:
                        url = Path(url).as_posix()
                    yield File.photo(file=url)
                case MessageSegmentType.text.value:
                    yield Entity.text(text=data.get('text'))
                case _:
                    pass

    def _build(self, message: Union[str, None, OmegaMessage, OmegaMessageSegment]) -> TelegramMessage:
        _msg = TelegramMessage()
        if message is None:
            return _msg
        elif isinstance(message, str):
            return TelegramMessage(message)
        elif isinstance(message, OmegaMessageSegment):
            return TelegramMessage(self._construct(OmegaMessage(message)))
        elif isinstance(message, OmegaMessage):
            return TelegramMessage(self._construct(message))
        else:
            return TelegramMessage(message)


@register_extractor(adapter_name=SupportedPlatform.telegram.value)
class TelegramMessageExtractor(MessageExtractor):
    """Telegram 消息解析器"""

    @staticmethod
    def _construct(message: TelegramMessage) -> Iterable[OmegaMessageSegment]:

        def _iter_message(msg: TelegramMessage) -> Iterable[Tuple[str, dict]]:
            for seg in msg:
                yield seg.type, seg.data

        for type_, data in _iter_message(message):
            match type_:
                case 'mention':
                    yield OmegaMessageSegment.at(user_id=str(data.get('text')).removeprefix('@'))
                case 'photo':
                    yield OmegaMessageSegment.image(url=data.get('file'))
                case 'text':
                    yield OmegaMessageSegment.text(text=data.get('text'))
                case _:
                    pass

    def _build(self, message: Union[str, None, TelegramMessage, TelegramMessageSegment]) -> OmegaMessage:
        _msg = OmegaMessage()
        if message is None:
            return _msg
        elif isinstance(message, str):
            return OmegaMessage(message)
        elif isinstance(message, TelegramMessageSegment):
            return OmegaMessage(self._construct(TelegramMessage(message)))
        elif isinstance(message, TelegramMessage):
            return OmegaMessage(self._construct(message))
        else:
            return OmegaMessage(message)


class TelegramMessageSender(MessageSender):
    """Telegram 消息 Sender"""

    @classmethod
    def get_builder(cls) -> Type[MessageBuilder]:
        return TelegramMessageBuilder

    @classmethod
    def get_extractor(cls) -> Type[MessageExtractor]:
        return TelegramMessageExtractor

    def construct_multi_msgs(self, messages: Iterable[Union[str, None, TelegramMessage, TelegramMessageSegment]]):
        send_message = TelegramMessage()

        for message in messages:
            if isinstance(message, (str, TelegramMessageSegment)):
                send_message.append(message)
            elif isinstance(message, TelegramMessage):
                send_message.extend(message)
            else:
                pass

        return send_message

    def to_send_msg(self) -> SenderParams:
        raise NotImplementedError

    def to_send_multi_msgs(self) -> SenderParams:
        raise NotImplementedError

    def parse_revoke_sent_params(self, content: Any) -> Union[RevokeParams, Iterable[RevokeParams]]:
        if isinstance(content, list):
            return (
                RevokeParams(
                    api='delete_message',
                    params={'chat_id': x.chat.id, 'message_id': x.message_id}
                )
                for x in content
            )
        else:
            return RevokeParams(
                api='delete_message',
                params={'chat_id': content.chat.id, 'message_id': content.message_id}
            )


@register_sender(target_entity=SupportedTarget.telegram_user.value)
class TelegramUserMessageSender(TelegramMessageSender):
    """Telegram 用户消息 Sender"""

    def to_send_msg(self) -> SenderParams:
        return SenderParams(
            api='send_to',
            message_param_name='message',
            params={
                'chat_id': self.target_entity.entity_id
            }
        )

    def to_send_multi_msgs(self) -> SenderParams:
        return self.to_send_msg()


@register_sender(target_entity=SupportedTarget.telegram_group.value)
class TelegramGroupMessageSender(TelegramMessageSender):
    """Telegram 群组消息 Sender"""

    def to_send_msg(self) -> SenderParams:
        return SenderParams(
            api='send_to',
            message_param_name='message',
            params={
                'chat_id': self.target_entity.entity_id
            }
        )

    def to_send_multi_msgs(self) -> SenderParams:
        return self.to_send_msg()


@register_sender(target_entity=SupportedTarget.telegram_channel.value)
class TelegramChannelMessageSender(TelegramMessageSender):
    """Telegram 频道消息 Sender"""

    def to_send_msg(self) -> SenderParams:
        return SenderParams(
            api='send_to',
            message_param_name='message',
            params={
                'chat_id': self.target_entity.entity_id
            }
        )

    def to_send_multi_msgs(self) -> SenderParams:
        return self.to_send_msg()


@register_event_handler(event=TelegramMessageEvent)
class TelegramMessageEventHandler(EventHandler):
    """Telegram 消息事件处理器"""

    async def send_at_sender(self, message: Union[str, None, TelegramMessage, TelegramMessageSegment], **kwargs):
        self.event = cast(TelegramMessageEvent, self.event)

        full_message = TelegramMessage()

        if isinstance(self.event, (TelegramPrivateMessageEvent, TelegramGroupMessageEvent)):
            full_message += Entity.mention(f'@{self.event.from_.username}') + " "
        else:
            pass

        full_message += message

        return await self.bot.send(event=self.event, message=full_message, **kwargs)

    async def send_reply(self, message: Union[str, None, TelegramMessage, TelegramMessageSegment], **kwargs):
        self.event = cast(TelegramMessageEvent, self.event)
        return await self.bot.send(
            event=self.event, message=message, reply_to_message_id=self.event.message_id, **kwargs
        )


@register_entity_depend(event=TelegramEvent)
class TelegramEventEntityDepend(EntityDepend):
    """Telegram 事件 Entity 对象依赖类"""

    @classmethod
    def extract_event_entity_from_event(cls, bot: TelegramBot, event: TelegramEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_user', entity_id=bot.self_id, parent_id=bot.self_id
        )

    @classmethod
    def extract_user_entity_from_event(cls, bot: TelegramBot, event: TelegramEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_user', entity_id=bot.self_id, parent_id=bot.self_id
        )


@register_entity_depend(event=TelegramGroupMessageEvent)
class TelegramGroupMessageEventEntityDepend(EntityDepend):
    """Telegram 群组消息事件 Entity 对象依赖类"""

    @classmethod
    def extract_event_entity_from_event(cls, bot: TelegramBot, event: TelegramGroupMessageEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_group',
            entity_id=str(event.chat.id), parent_id=bot.self_id,
            entity_name=event.chat.title, entity_info=event.chat.type
        )

    @classmethod
    def extract_user_entity_from_event(cls, bot: TelegramBot, event: TelegramGroupMessageEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_user',
            entity_id=str(event.from_.id), parent_id=bot.self_id,
            entity_name=event.from_.first_name,
            entity_info=f'{event.from_.first_name}/{event.from_.last_name}, @{event.from_.username}'
        )


@register_entity_depend(event=TelegramPrivateMessageEvent)
class TelegramPrivateMessageEventEntityDepend(EntityDepend):
    """Telegram 私聊消息事件 Entity 对象依赖类"""

    @classmethod
    def extract_event_entity_from_event(cls, bot: TelegramBot, event: TelegramPrivateMessageEvent) -> EntityParams:
        return cls.extract_user_entity_from_event(bot=bot, event=event)

    @classmethod
    def extract_user_entity_from_event(cls, bot: TelegramBot, event: TelegramPrivateMessageEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_user',
            entity_id=str(event.from_.id), parent_id=bot.self_id,
            entity_name=event.from_.first_name,
            entity_info=f'{event.from_.first_name}/{event.from_.last_name}, @{event.from_.username}'
        )


@register_entity_depend(event=TelegramChannelPostEvent)
class TelegramChannelPostEventEntityDepend(EntityDepend):
    """Telegram 频道事件 Entity 对象依赖类"""

    @classmethod
    def extract_event_entity_from_event(cls, bot: TelegramBot, event: TelegramChannelPostEvent) -> EntityParams:
        return EntityParams(
            bot_id=bot.self_id, entity_type='telegram_channel',
            entity_id=str(event.chat.id), parent_id=bot.self_id,
            entity_name=event.chat.title, entity_info=event.chat.type
        )

    @classmethod
    def extract_user_entity_from_event(cls, bot: TelegramBot, event: TelegramChannelPostEvent) -> EntityParams:
        return cls.extract_event_entity_from_event(bot=bot, event=event)


__all__ = []
