"""
@Author         : Ailitonia
@Date           : 2021/07/17 22:36
@FileName       : omega_recaller.py
@Project        : nonebot2_miya
@Description    : 快速撤回 bot 发送的消息
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command

from src.params.depends import EVENT_MATCHER_INTERFACE
from src.service import enable_processor_state


@on_command(
    'self-recall',
    aliases={'撤回'},
    permission=SUPERUSER,
    priority=10,
    block=True,
    state=enable_processor_state(name='SelfRecall', enable_processor=False),
).handle()
async def handle_self_recall(interface: EVENT_MATCHER_INTERFACE) -> None:
    reply_msg_id = interface.get_event_reply_msg_id()
    if not reply_msg_id:
        return

    try:
        await interface.revoke_current_session_msg(message_id=reply_msg_id)
        logger.success(f'SelfRecall | 撤回了{interface.bot}消息(message_id={reply_msg_id!r})')
    except Exception as e:
        logger.error(f'SelfRecall | 撤回{interface.bot}消息(message_id={reply_msg_id!r})失败, {e!r}')
        await interface.finish_reply('撤回消息部分或全部失败了, 请检查是否有撤回权限')


__all__ = []
