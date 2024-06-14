from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import RegexDict

from src.service import OmegaInterface
from .data_source import mix_emoji


async def handle_emoji_mix(msg: dict = RegexDict()):
    interface = OmegaInterface()

    emoji_code1 = msg["code1"]
    emoji_code2 = msg["code2"]
    result = await mix_emoji(emoji_code1, emoji_code2)
    if isinstance(result, str):
        await interface.finish(result)
    else:
        await interface.finish(MessageSegment.image(result))
