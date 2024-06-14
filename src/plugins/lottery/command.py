"""
@Author         : Ailitonia
@Date           : 2023/10/18 23:23
@FileName       : command
@Project        : nonebot2_miya
@Description    : 
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

import re
import random
from typing import Annotated

from nonebot.params import ArgStr
from nonebot.plugin import on_command

from src.params.handler import get_command_str_single_arg_parser_handler
from src.service import OmegaInterface, enable_processor_state

from nonebot.adapters.onebot.v11 import (
    Bot as OneBotV11Bot,
    GroupMessageEvent as OneBotV11GroupMessageEvent,
)


@on_command(
    'lottery',
    aliases={'抽奖'},
    handlers=[get_command_str_single_arg_parser_handler('expression')],
    priority=10,
    block=True,
    state=enable_processor_state(name='Lottery', level=10),
).got('expression', prompt='请输入抽奖人数')
async def handle_lottery(expression: Annotated[str, ArgStr('expression')], event: OneBotV11GroupMessageEvent,
                         bot: OneBotV11Bot):
    _lottery = expression.strip()
    interface = OmegaInterface()

    if re.match(r'^\d+$', _lottery):
        people_num = int(_lottery)

        # interface.get_bot().call_api(api='get_group_member_list', group_id=event.group_id)
        group_member_list = await bot.call_api(api='get_group_member_list', group_id=event.group_id)
        group_user_name_list = []

        for user_info in group_member_list:
            # 用户信息
            user_nickname = user_info['nickname']
            user_group_nickmane = user_info['card']
            if not user_group_nickmane:
                user_group_nickmane = user_nickname
            group_user_name_list.append(user_group_nickmane)

        if people_num > len(group_user_name_list):
            await interface.finish(f'【错误】抽奖人数大于群成员人数了QAQ')

        lottery_result = random.sample(group_user_name_list, k=people_num)
        msg = '【' + str.join('】\n【', lottery_result) + '】'
        await interface.finish(f"抽奖人数: 【{people_num}】\n以下是中奖名单:\n{msg}")
    else:
        await interface.finish(f'格式不对呢, 人数应该是数字')


__all__ = []
