from typing import Annotated

import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    PrivateMessageEvent,
    MessageEvent,
    helpers,
)
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.exception import FinishedException
from nonebot.params import ArgStr
from nonebot.plugin import on_message
from nonebot.rule import to_me
from openai import AsyncOpenAI

from src.params.handler import get_command_str_single_arg_parser_handler
from src.service import OmegaInterface
from src.service import enable_processor_state
from .config import Config, ConfigError

plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if not plugin_config.api_key:
    raise ConfigError("请配置大模型使用的KEY")
if plugin_config.api_url:
    client = AsyncOpenAI(
        api_key=plugin_config.api_key, base_url=plugin_config.api_url
    )
else:
    client = AsyncOpenAI(api_key=plugin_config.api_key)

model_id = plugin_config.api_model

# public = plugin_config.chatgpt_turbo_public
session = {}
session_lock = {}


async def chat_handle(event: MessageEvent, msg: str, session_id: str = None):
    interface = OmegaInterface()

    if session_id is not None:
        pass
    elif isinstance(event, GroupMessageEvent):
        session_id = str(event.get_session_id())
    elif isinstance(event, PrivateMessageEvent):
        session_id = 'private_chat_' + str(event.get_session_id())

    if session_lock.get(session_id, False):
        await interface.finish("上一条消息还未处理完毕，请稍后再试！", at_sender=True)

    # 简单锁
    session_lock[session_id] = True

    content = msg.strip()
    # 多模态 to do
    img_url = helpers.extract_image_urls(event.message)
    if content == "" or content is None:
        session_lock[session_id] = False
        await interface.finish(MessageSegment.text("内容不能为空哦～"), at_sender=True)

    # 初始化
    if session.get(session_id) is None:
        session[session_id] = []

    try:
        check_session_length(session_id, "user", content)
        response = await client.chat.completions.create(
            model=model_id,
            messages=session[session_id],
            stream=False
        )
    except Exception as error:
        session_lock[session_id] = False
        await interface.finish(str(error), at_sender=True)
    try:
        assistant_res = str(response.choices[0].message.content)
        check_session_length(session_id, "assistant", assistant_res)
        session_lock[session_id] = False
    except Exception as error:
        session_lock[session_id] = False
        await interface.finish(str(error), at_sender=True)

    await interface.finish(MessageSegment.text(assistant_res), at_sender=True)


@on_command(
    'chat',
    handlers=[get_command_str_single_arg_parser_handler('chat_msg')],
    priority=15,
    block=True,
    state=enable_processor_state(name='chat', level=10, cooldown=5),
).got('chat_msg', prompt='有啥想说的?')
async def _(event: MessageEvent, msg: Annotated[str, ArgStr('chat_msg')]):
    interface = OmegaInterface()
    # 若未开启私聊模式则检测到私聊就结束
    if isinstance(event, PrivateMessageEvent) and not plugin_config.enable_private_chat:
        interface.finish("对不起，私聊暂不支持此功能。")

    await chat_handle(event, msg)


async def handle_ignore_msg(bot: Bot, event: GroupMessageEvent):
    """忽略特殊类型的消息"""
    msg = event.get_plaintext()
    for command_start in bot.config.command_start:
        if msg.startswith(command_start):
            raise FinishedException
    if msg.startswith('!SU'):
        raise FinishedException


# 不带记忆的对话
@on_message(
    rule=to_me(),
    permission=GROUP,
    handlers=[handle_ignore_msg],
    priority=80,
    block=True,
    state=enable_processor_state('chat', enable_processor=False, cooldown=2, echo_processor_result=True)
).handle()
async def _(event: GroupMessageEvent):
    interface = OmegaInterface()

    img_url = helpers.extract_image_urls(event.message)
    content = event.get_plaintext()
    if content == "" or content is None:
        await interface.finish(MessageSegment.text("内容不能为空哦～"), at_sender=True)

    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": content}],
            stream=False
        )
    except Exception as error:
        await interface.finish(str(error), at_sender=True)
    await interface.finish(
        MessageSegment.text(str(response.choices[0].message.content)),
        at_sender=True,
    )


@on_command(
    'clear',
    priority=15,
    block=True,
    state=enable_processor_state(name='chat', level=10),
).handle()
async def _(event: MessageEvent):
    del session[event.get_session_id()]
    interface = OmegaInterface()
    await interface.finish(
        MessageSegment.text("成功清除历史记录！"), at_sender=True
    )


@on_command(
    'gchat',
    handlers=[get_command_str_single_arg_parser_handler('chat_msg')],
    priority=15,
    block=True,
    state=enable_processor_state(name='chat', level=10, cooldown=5),
).got('chat_msg', prompt='有啥想说的?')
async def _(event: GroupMessageEvent, msg: Annotated[str, ArgStr('chat_msg')]):
    interface = OmegaInterface()
    # 若未开启私聊模式则检测到私聊就结束
    if isinstance(event, PrivateMessageEvent):
        interface.finish("直接使用/chat <想要发送的内容> 即可哦～")

    await chat_handle(event, msg, session_id='gchat_' + str(event.group_id))


# check session 中某个 id 的所有context的长度, 如果超过 128K 则移除最早的context，直到加入最新的 context 后小于 128K
def check_session_length(session_id, role, context):
    total_length = 0
    if session[session_id] is None:
        session[session_id] = []
        session[session_id].append({"role": role, "content": context})
    else:
        session[session_id].append({"role": role, "content": context})
        for i in session[session_id]:
            total_length += len(i['content'])
        while total_length > 128000:
            pop = session[session_id].pop(0)
            total_length -= len(pop['content'])


@on_command(
    'gclear',
    priority=15,
    block=True,
    state=enable_processor_state(name='chat', level=10),
).handle()
async def _(event: GroupMessageEvent):
    session_id = 'gchat_' + str(event.group_id)
    try:
        del session[session_id]
        del session_lock[session_id]
    except Exception as error:
        session[session_id] = []
        session_lock[session_id] = False
    interface = OmegaInterface()
    await interface.finish(
        MessageSegment.text("成功清除群接龙历史记录！"), at_sender=True
    )
