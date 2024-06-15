from typing import Literal

from src.service import scheduler
from .helper import drink_manager

_MONITOR_JOB_ID: Literal['drink_reminder_scheduler'] = 'drink_reminder_scheduler'
"""动态检查的定时任务 ID"""


async def drink_reminder_scheduler() -> None:
    await drink_manager.drink_reminder()


scheduler.add_job(
    drink_reminder_scheduler,
    'cron',
    # year=None,
    # month=None,
    # day='*/1',
    # week=None,
    # day_of_week=None,
    hour="8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
    # minute='*/1',
    # second='*/5',
    # start_date=None,
    # end_date=None,
    # timezone=None,
    id=_MONITOR_JOB_ID,
    coalesce=True,
    misfire_grace_time=120
)

__all__ = [
    'scheduler'
]
