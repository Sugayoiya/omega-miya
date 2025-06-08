"""
@Author         : Ailitonia
@Date           : 2022/05/03 19:41
@FileName       : monitor.py
@Project        : nonebot2_miya
@Description    : Bilibili Live monitor
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot import get_driver, logger

from src.service import scheduler
from src.utils import run_async_with_time_limited, semaphore_gather
from .subscription_source import BilibiliLiveRoomSubscriptionManager


@get_driver().on_startup
async def _init_all_live_room_subscription_source_status() -> None:
    """启动时初始化所有订阅源中直播间的状态"""
    logger.opt(colors=True).info('<lc>BilibiliLiveRoomMonitor</lc> | Initializing live room status')

    try:
        room_ids = await BilibiliLiveRoomSubscriptionManager.query_all_subscribed_sub_source_ids()
        init_tasks = [
            BilibiliLiveRoomSubscriptionManager(room_id).query_live_room_status()
            for room_id in room_ids
        ]
        await semaphore_gather(tasks=init_tasks, semaphore_num=16, return_exceptions=False)
        logger.opt(colors=True).success('<lc>BilibiliLiveRoomMonitor</lc> | Live room status initializing completed')
    except Exception as e:
        logger.error(f'BilibiliLiveRoomMonitor | Live room status initializing failed, {e!r}')
        raise e


@run_async_with_time_limited(delay_time=120)
async def bili_live_room_update_monitor() -> None:
    """Bilibili 直播间订阅 直播间更新监控"""
    logger.debug('BilibiliLiveRoomSubscriptionMonitor | Started checking bilibili live room update')

    # 检查直播间更新并通知已订阅的用户或群组
    room_ids = await BilibiliLiveRoomSubscriptionManager.query_all_subscribed_sub_source_ids()
    if not room_ids:
        logger.debug('BilibiliLiveRoomSubscriptionMonitor | None of live room subscription, ignored')
        return

    # 处理直播间状态更新并向订阅者发送直播间更新信息
    send_tasks = [
        BilibiliLiveRoomSubscriptionManager(room_id).check_subscription_source_update_and_send_entity_message()
        for room_id in room_ids
    ]
    await semaphore_gather(tasks=send_tasks, semaphore_num=16)

    logger.debug('BilibiliLiveRoomSubscriptionMonitor | Bilibili user live room update checking completed')


scheduler.add_job(
    bili_live_room_update_monitor,
    'cron',
    # year=None,
    # month=None,
    # day='*/1',
    # week=None,
    # day_of_week=None,
    # hour=None,
    # minute='*/1',
    second='*/30',
    # start_date=None,
    # end_date=None,
    # timezone=None,
    id='bili_live_room_update_monitor',
    coalesce=True,
    max_instances=2,
    misfire_grace_time=60,
)


__all__ = [
    'scheduler',
]
