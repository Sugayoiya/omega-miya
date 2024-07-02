from typing import Annotated

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger
from nonebot.params import ArgStr
from nonebot.plugin import MatcherGroup
from nonebot.plugin import on_command

from src.params.handler import get_command_str_single_arg_parser_handler
from src.service import OmegaInterface, enable_processor_state
from .helper import get_image, pokemon_prompt_handle

pokemon_fusion = MatcherGroup(
    type='message',
    priority=10,
    block=True,
    state=enable_processor_state(name='pokemon_fusion', level=20, auth_node='pokemon_fusion',
                                 echo_processor_result=False),
)


@on_command(
    '融合',
    aliases={'宝可梦融合'},
    handlers=[get_command_str_single_arg_parser_handler('pokemons')],
    priority=10,
    block=True,
    state=enable_processor_state(name='pokemon_fusion', level=20),
).got('pokemons', prompt='想要融合什么宝可梦? 发来给你看看:')
async def handle_guess(pokemons: Annotated[str, ArgStr('pokemons')]):
    pokemons_list = pokemons.strip()
    interface = OmegaInterface()
    try:
        pokemon_ids = await pokemon_prompt_handle(pokemons_list)
        try:
            if isinstance(pokemon_ids, list):
                msgs = [MessageSegment.image(await get_image(pokemon_id)) for pokemon_id in pokemon_ids]
                await interface.finish(Message(msgs))
            elif isinstance(pokemon_ids, str):
                await interface.finish(Message(pokemon_ids))
        except:
            pass
    except Exception as e:
        logger.error(f'pokemon fusion结果失败, {e!r}')
        await interface.send_reply('发生了意外的错误, 请稍后再试')
