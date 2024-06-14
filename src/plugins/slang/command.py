from typing import Annotated

from nonebot.params import ArgStr
from nonebot.plugin import on_command

from src.params.handler import get_command_str_single_arg_parser_handler
from src.service import OmegaInterface, enable_processor_state
from .helper import text_to_emoji


@on_command(
    '抽象话',
    aliases={'抽象'},
    handlers=[get_command_str_single_arg_parser_handler('expression')],
    priority=10,
    block=True,
    state=enable_processor_state(name='Roll', level=10),
).got('expression', prompt='你要发什么推?')
async def handle_slang(expression: Annotated[str, ArgStr('expression')]):
    expression = expression.strip()
    interface = OmegaInterface()

    abstract_responses = text_to_emoji(expression)
    if abstract_responses:
        await interface.finish(abstract_responses)
    else:
        await interface.finish("抽象异常了~一定是程序出了点问题！")


__all__ = []
