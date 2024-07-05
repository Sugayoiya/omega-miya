from dataclasses import dataclass

from nonebot import logger
from pydantic import ValidationError

from src.resource import StaticResource


@dataclass
class EmojiMixConfig:
    # emoji data path
    emoji_json: StaticResource = StaticResource('docs', 'emoji_mix', 'metadata.json')


try:
    emoji_data = EmojiMixConfig()
except ValidationError as e:
    import sys

    logger.opt(colors=True).critical(f"Failed to load emoji_mix config: {e}")
    sys.exit(f'Failed to load emoji_mix config: {e}')

__all__ = ['emoji_data']
