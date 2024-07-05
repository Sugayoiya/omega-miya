import re

import emoji
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import RegexDict
from nonebot.plugin import MatcherGroup
from nonebot.plugin import on_command

from src.service import OmegaInterface
from src.service import OmegaRequests
from src.service import enable_processor_state
from .helper import EmojiMixManager

emojis = emoji.EMOJI_DATA.keys()
pattern = "(" + "|".join(re.escape(e) for e in emojis) + ")"

emoji_mix = MatcherGroup(
    type='message',
    priority=10,
    block=True,
    state=enable_processor_state(name='emoji_mix', level=10, auth_node='emoji_mix', echo_processor_result=False),
)

emoji_mix_manager = EmojiMixManager()


async def handle_emoji_mix(msg: dict = RegexDict()):
    interface = OmegaInterface()

    e1 = msg['code1']
    e2 = msg['code2']
    try:
        url = emoji_mix_manager.get_combination_url(e1, e2)
    except Exception as e:
        await interface.finish(f'{e}')

    if not url:
        await interface.finish(f'不支持的emoji组合:{e1}+{e2}')

    res = await OmegaRequests(timeout=10).get(url=url)
    if res.status_code != 200:
        await interface.send('emoji融合出错，请稍后再试')
        return

    await interface.send(MessageSegment.image(res.content))


emoji_mix.on_regex(
    rf"^\s*(?P<code1>{pattern})\s*\+\s*(?P<code2>{pattern})\s*$",
    handlers=[handle_emoji_mix])


@on_command(
    'emoji合成',
    priority=10,
    block=True,
    state=enable_processor_state(name='emoji_mix', level=10, auth_node='emoji_mix', echo_processor_result=False),
).handle()
async def handle_guess():
    interface = OmegaInterface()
    combination = emoji_mix_manager.get_random_combination()

    e1 = combination['leftEmoji']
    e2 = combination['rightEmoji']
    url = combination['gStaticUrl']

    res = await OmegaRequests(timeout=10).get(url=url)
    if res.status_code != 200:
        await interface.send('emoji融合出错，请稍后再试')
        return

    await interface.send(MessageSegment.image(res.content) + f'\n随机融合by{e1} + {e2}')
