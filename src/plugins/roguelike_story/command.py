"""
@Author         : Ailitonia
@Date           : 2025/2/16 21:39
@FileName       : command
@Project        : omega-miya
@Description    : 故事肉鸽插件
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from datetime import timedelta
from typing import Annotated

from nonebot.exception import MatcherException
from nonebot.log import logger
from nonebot.params import ArgStr, Depends
from nonebot.plugin import CommandGroup

from src.params.handler import get_command_str_single_arg_parser_handler
from src.service import OmegaMatcherInterface as OmMI
from src.service import enable_processor_state
from .helpers import handle_story_init, handle_story_continue
from .session import get_story_session, remove_story_session

roguelike_story = CommandGroup(
    'roguelike-story',
    block=True,
    state=enable_processor_state(
        name='RoguelikeStory',
        level=30,
        cooldown=60,
    ),
)


@roguelike_story.command(
    'start',
    aliases={'故事肉鸽启动', '肉鸽故事启动', '继续故事肉鸽', '继续肉鸽故事'},
    handlers=[get_command_str_single_arg_parser_handler('description', ensure_key=True)],
    expire_time=timedelta(minutes=5),
).got('description')
async def handle_story_start(
        interface: Annotated[OmMI, Depends(OmMI.depend('event'))],
        description: Annotated[str | None, ArgStr('description')],
) -> None:
    try:
        story_session = get_story_session(interface=interface)
    except Exception as e:
        logger.warning(f'Roguelike Story | {interface.entity}获取故事会话失败, {e}')
        await interface.finish_reply(f'获取故事会话失败, 请稍后再试或联系管理员处理')

    try:
        if not story_session.is_inited:
            await handle_story_init(story_session=story_session, interface=interface, description=description)
        else:
            await handle_story_continue(story_session=story_session, interface=interface, description=description)
    except MatcherException:
        raise
    except Exception as e:
        logger.warning(f'Roguelike Story | 生成失败, {e}')
        await interface.finish_reply(f'肉鸽姬还没有想好接下来会发生什么, 请稍后再试QAQ')


@roguelike_story.command(
    'remove',
    aliases={'结束故事肉鸽', '结束肉鸽故事', '故事肉鸽重开', '肉鸽故事重开'},
    handlers=[get_command_str_single_arg_parser_handler('ensure', ensure_key=True)],
).got('description')
async def handle_story_remove(
        interface: Annotated[OmMI, Depends(OmMI.depend('event'))],
        ensure: Annotated[str | None, ArgStr('ensure')],
) -> None:
    try:
        if ensure is None:
            await interface.reject_arg_reply('ensure', '你确认要终结这个肉鸽故事吗？\n【是/否】')
        elif ensure in ['是', '确认', 'Yes', 'yes', 'Y', 'y']:
            remove_story_session(interface=interface)
            await interface.finish_reply('目前的肉鸽故事已移除，你可以重新开始新的冒险了~')
        else:
            await interface.finish_reply('已取消操作')
    except MatcherException:
        raise
    except Exception as e:
        logger.warning(f'Roguelike Story | {interface.entity}获取故事会话失败, {e}')
        await interface.finish_reply(f'获取故事会话失败, 请稍后再试或联系管理员处理')


__all__ = []
