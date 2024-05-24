"""
@Author         : Ailitonia
@Date           : 2023/3/19 14:45
@FileName       : telegram
@Project        : nonebot2_miya
@Description    : Telegram support
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from typing import Annotated

from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.params import Depends
from nonebot.adapters.telegram.bot import Bot

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from src.database import BotSelfDAL, get_db_session
from src.service.omega_base.event import BotConnectEvent, BotDisconnectEvent


@event_preprocessor
async def __telegram_bot_connect(
        bot: Bot,
        event: BotConnectEvent,
        session: Annotated[AsyncSession, Depends(get_db_session)]
) -> None:
    """处理 Telegram Bot 连接事件"""
    assert str(bot.self_id) == str(event.bot_id), 'Bot self_id not match BotActionEvent bot_id'

    bot_dal = BotSelfDAL(session=session)

    # 更新 bot 状态
    bot_info = await bot.get_me()

    info = '||'.join([f'{k}:{v}' for (k, v) in bot_info.model_dump().items()])
    try:
        exist_bot = await bot_dal.query_unique(self_id=bot.self_id)
        await bot_dal.update(id_=exist_bot.id, bot_type=event.bot_type, bot_status=1, bot_info=info)
        logger.opt(colors=True).success(f'{event.bot_type}: <lg>{bot.self_id} 已连接</lg>, Bot status upgraded Success')
    except NoResultFound:
        await bot_dal.add(self_id=bot.self_id, bot_type=event.bot_type, bot_status=1, bot_info=info)
        logger.opt(colors=True).success(f'{event.bot_type}: <lg>{bot.self_id} 已连接</lg>, Bot status added Success')


@event_preprocessor
async def __telegram_bot_disconnect(
        bot: Bot,
        event: BotDisconnectEvent,
        session: Annotated[AsyncSession, Depends(get_db_session)]
) -> None:
    """处理 Telegram Bot 断开连接事件"""
    assert str(bot.self_id) == str(event.bot_id), 'Bot self_id not match BotActionEvent bot_id'

    bot_dal = BotSelfDAL(session)
    try:
        exist_bot = await bot_dal.query_unique(self_id=bot.self_id)
        await bot_dal.update(id_=exist_bot.id, bot_type=event.bot_type, bot_status=0)
        logger.opt(colors=True).success(f'{event.bot_type}: <ly>{bot.self_id} 已离线</ly>, Bot status upgraded Success')
    except NoResultFound:
        await bot_dal.add(self_id=bot.self_id, bot_type=event.bot_type, bot_status=0)
        logger.opt(colors=True).success(f'{event.bot_type}: <ly>{bot.self_id} 已离线</ly>, Bot status added Success')


__all__ = []