"""
@Author         : Ailitonia
@Date           : 2023/8/4 2:50
@FileName       : command
@Project        : nonebot2_miya
@Description    : Bilibili 直播间订阅
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from typing import Annotated

from nonebot.log import logger
from nonebot.params import ArgStr, Depends
from nonebot.plugin import CommandGroup

from src.params.handler import get_command_str_single_arg_parser_handler, get_set_default_state_handler
from src.params.permission import IS_ADMIN
from src.service import OmegaInterface, enable_processor_state
from src.utils.bilibili_api import BilibiliLiveRoom
from src.utils.bilibili_api.exception import BilibiliApiError

from .consts import NOTICE_AT_ALL
from .monitor import scheduler
from .helpers import add_live_room_sub, delete_live_room_sub, query_subscribed_live_room_sub_source


bili_live = CommandGroup(
    'bili_live',
    permission=IS_ADMIN,
    priority=20,
    block=True,
    state=enable_processor_state(
        name='BilibiliLiveRoomSubscriptionManager',
        level=20,
        extra_auth_node={NOTICE_AT_ALL}
    ),
)


@bili_live.command(
    'add-subscription',
    aliases={'B站直播间订阅', 'b站直播间订阅', 'Bilibili直播间订阅', 'bilibili直播间订阅'},
    handlers=[
        get_set_default_state_handler('ensure', value=None),
        get_command_str_single_arg_parser_handler('room_id', ensure_key=True)
    ]
).got('ensure')
async def handle_add_subscription(
        interface: Annotated[OmegaInterface, Depends(OmegaInterface())],
        ensure: Annotated[str | None, ArgStr('ensure')],
        room_id: Annotated[str | None, ArgStr('room_id')]
) -> None:
    interface.refresh_matcher_state()

    # 检查是否收到确认消息后执行新增订阅
    if ensure is None:
        pass
    elif ensure in ['是', '确认', 'Yes', 'yes', 'Y', 'y']:
        await interface.send_at_sender('正在更新Bilibili直播间订阅信息, 请稍候')

        room = BilibiliLiveRoom(room_id=int(room_id))
        scheduler.pause()  # 暂停计划任务避免中途检查更新
        try:
            await add_live_room_sub(interface=interface, live_room=room)
            await interface.entity.commit_session()
            logger.success(f'{interface.entity}订阅直播间{room}成功')
            msg = f'订阅直播间{room_id}成功'
        except Exception as e:
            logger.error(f'{interface.entity}订阅直播间{room}失败, {e!r}')
            msg = f'订阅直播间{room_id}失败, 可能是网络异常或发生了意外的错误, 请稍后再试或联系管理员处理'
        scheduler.resume()
        await interface.send_at_sender(msg)
        return
    else:
        await interface.send_at_sender('已取消操作')
        return

    # 未收到确认消息后则为首次触发命令执行直播间信息检查
    if room_id is None:
        await interface.send_at_sender('未提供直播间房间号参数, 已取消操作')
        return
    room_id = room_id.strip()
    if not room_id.isdigit():
        await interface.send_at_sender('非有效的直播间房间号, 直播间房间号应当为纯数字, 已取消操作')
        return

    try:
        room = BilibiliLiveRoom(room_id=int(room_id))
        live_room_data = await room.query_live_room_data()
        if live_room_data.error:
            raise BilibiliApiError(f'query {room} data failed, {live_room_data.message}')

        live_room_user_data = await room.query_live_room_user_data()
        if live_room_user_data.error:
            raise BilibiliApiError(f'query {room} user data failed, {live_room_user_data.message}')

        # 针对直播间短号进行处理
        if room_id == str(live_room_data.data.short_id) and room_id != str(live_room_data.data.room_id):
            logger.debug(f'订阅直播间短号{room_id}, 已转换为直播间房间号{live_room_data.data.room_id}')
            interface.matcher.state.update({'room_id': live_room_data.data.room_id})

    except Exception as e:
        logger.error(f'获取直播间{room_id}用户信息失败, {e!r}')
        await interface.send_at_sender('获取直播间用户信息失败, 可能是网络原因或没有这个直播间, 请稍后再试')
        return

    ensure_msg = f'即将订阅Bilibili用户【{live_room_user_data.data.name}】的直播间\n\n确认吗?\n【是/否】'
    await interface.send_at_sender(ensure_msg)
    await interface.matcher.reject_arg('ensure')


@bili_live.command(
    'del-subscription',
    aliases={'取消B站直播间订阅', '取消b站直播间订阅', '取消Bilibili直播间订阅', '取消bilibili直播间订阅'},
    handlers=[
        get_set_default_state_handler('ensure', value=None),
        get_command_str_single_arg_parser_handler('room_id', ensure_key=True)
    ]
).got('ensure')
async def handle_del_subscription(
        interface: Annotated[OmegaInterface, Depends(OmegaInterface())],
        ensure: Annotated[str | None, ArgStr('ensure')],
        room_id: Annotated[str | None, ArgStr('room_id')]
) -> None:
    interface.refresh_matcher_state()

    # 检查是否收到确认消息后执行删除订阅
    if ensure is None:
        pass
    elif ensure in ['是', '确认', 'Yes', 'yes', 'Y', 'y']:
        try:
            await delete_live_room_sub(interface=interface, room_id=int(room_id))
            await interface.entity.commit_session()
            logger.success(f'{interface.entity}取消订阅直播间(rid={room_id})成功')
            msg = f'取消订阅直播间{room_id}成功'
        except Exception as e:
            logger.error(f'{interface.entity}取消订阅直播间(rid={room_id})失败, {e!r}')
            msg = f'取消订阅直播间{room_id}失败, 请稍后再试或联系管理员处理'

        await interface.send_at_sender(msg)
        return
    else:
        await interface.send_at_sender('已取消操作')
        return

    # 未收到确认消息后则为首次触发命令执行直播间信息检查
    if room_id is None:
        await interface.send_at_sender('未提供直播间房间号参数, 已取消操作')
        return
    room_id = room_id.strip()
    if not room_id.isdigit():
        await interface.send_at_sender('非有效的直播间房间号, 直播间房间号应当为纯数字, 已取消操作')
        return

    try:
        exist_sub = await query_subscribed_live_room_sub_source(interface=interface)
        if room_id in exist_sub.keys():
            ensure_msg = f'取消订阅Bilibili用户【{exist_sub.get(room_id)}】的直播间\n\n确认吗?\n【是/否】'
            reject_key = 'ensure'
        else:
            exist_text = '\n'.join(f'{sub_id}: {user_nickname}' for sub_id, user_nickname in exist_sub.items())
            ensure_msg = f'未订阅直播间{room_id}, 请确认已订阅的直播间列表:\n\n{exist_text if exist_text else "无"}'
            reject_key = None
    except Exception as e:
        logger.error(f'获取{interface.entity}已订阅直播间失败, {e!r}')
        await interface.send_at_sender('获取已订阅直播间列表失败, 请稍后再试或联系管理员处理')
        return

    await interface.send_at_sender(ensure_msg)
    if reject_key is not None:
        await interface.matcher.reject_arg(reject_key)
    else:
        await interface.matcher.finish()


@bili_live.command(
    'list-subscription',
    aliases={'B站直播间订阅列表', 'b站直播间订阅列表', 'Bilibili直播间订阅列表', 'bilibili直播间订阅列表'},
    permission=None,
    priority=10
).handle()
async def handle_list_subscription(interface: Annotated[OmegaInterface, Depends(OmegaInterface())]) -> None:
    interface.refresh_matcher_state()

    try:
        exist_sub = await query_subscribed_live_room_sub_source(interface=interface)
        exist_text = '\n'.join(f'{sub_id}: {user_nickname}' for sub_id, user_nickname in exist_sub.items())
        await interface.send_at_sender(f'当前已订阅的Bilibili直播间:\n\n{exist_text if exist_text else "无"}')
    except Exception as e:
        logger.error(f'获取{interface.entity}已订阅直播间失败, {e!r}')
        await interface.send_at_sender('获取已订阅直播间列表失败, 请稍后再试或联系管理员处理')


__all__ = []
