"""
@Author         : Ailitonia
@Date           : 2023/7/9 1:09
@FileName       : command
@Project        : nonebot2_miya
@Description    : 签到命令
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot.plugin import MatcherGroup

from src.service import enable_processor_state
from .config import eat_config
from .helper import what2eat, what2drink

eat = MatcherGroup(
    type='message',
    priority=10,
    block=True,
    state=enable_processor_state(name='eat', level=20, auth_node='eat', echo_processor_result=False),
)

eat.on_command('今天吃什么', handlers=[what2eat])
eat.on_command('今天喝什么', handlers=[what2drink])

if eat_config.eat_enable_regex_matcher:
    eat.on_regex(r"^(今天|[早中午晚][上饭餐午]|早上|夜宵|今晚)吃(什么|啥|点啥)$", handlers=[what2eat])
    eat.on_regex(r"^(今天|[早中午晚][上饭餐午]|早上|夜宵|今晚)喝(什么|啥|点啥)$", handlers=[what2drink])

__all__ = []
