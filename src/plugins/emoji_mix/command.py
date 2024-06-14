import re

import emoji
from nonebot.plugin import MatcherGroup

from src.service import enable_processor_state
from .helper import handle_emoji_mix

emojis = filter(lambda e: len(e) == 1, emoji.EMOJI_DATA.keys())
pattern = "(" + "|".join(re.escape(e) for e in emojis) + ")"

emoji_mix = MatcherGroup(
    type='message',
    priority=10,
    block=True,
    state=enable_processor_state(name='emoji_mix', level=20, auth_node='emoji_mix', echo_processor_result=False),
)

emoji_mix.on_regex(
    rf"^\s*(?P<code1>{pattern})\s*\+\s*(?P<code2>{pattern})\s*$",
    handlers=[handle_emoji_mix])
