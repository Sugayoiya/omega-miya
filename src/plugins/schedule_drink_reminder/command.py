from src.params.permission import IS_ADMIN
from nonebot.plugin import MatcherGroup

from src.params.permission import IS_ADMIN
from src.service import enable_processor_state
from .helper import drink_reminder_on, drink_reminder_off

drink_on = MatcherGroup(
    type='message',
    permission=IS_ADMIN,
    priority=20,
    block=True,
    state=enable_processor_state(
        name='drink_reminder'
    ),
)
drink_off = MatcherGroup(
    type='message',
    permission=IS_ADMIN,
    priority=20,
    block=True,
    state=enable_processor_state(
        name='drink_reminder'
    ),
)

drink_on.on_command('开启喝水小助手', handlers=[drink_reminder_on])
drink_off.on_command('关闭喝水小助手', handlers=[drink_reminder_off])
