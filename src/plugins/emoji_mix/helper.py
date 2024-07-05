import json
import random
from typing import Dict, Any, Optional

from nonebot import logger

from src.resource import TemporaryResource
from .config import emoji_data


def _format_hex_list(hex_list):
    return '-'.join(h.replace('0x', '') for h in hex_list)


def _get_emoji_hex_str(emoji_str):
    return _format_hex_list([hex(ord(char)) for char in emoji_str])


def _load_config(file: TemporaryResource) -> Optional[Dict[str, Any]]:
    if file.is_file:
        logger.debug(f'loading emoji data form {file}')
        with file.open('r', encoding='utf8') as f:
            return json.loads(f.read())
    else:
        return None


class EmojiMixManager:
    # {
    #     "knownSupportedEmoji": [
    #         "1fa84",
    #         "1f600",
    #         "1f603",
    #         "1f604",
    #         "1f601"],
    #     "data": {
    #         "2615": {
    #             "alt": "coffee",
    #             "emoji": "☕",
    #             "emojiCodepoint": "2615",
    #             "gBoardOrder": 378,
    #             "keywords": [
    #                 "hot_beverage",
    #                 "beverage",
    #                 "caffeine",
    #                 "latte",
    #                 "espresso",
    #                 "coffee",
    #                 "mug"
    #             ],
    #             "category": "food & drink",
    #             "subcategory": "drink",
    #             "combinations": {
    #                 "2615": [
    #                     {
    #                         "gStaticUrl": "https://www.gstatic.com/android/keyboard/emojikitchen/20201001/u2615/u2615_u2615.png",
    #                         "alt": "coffee-coffee",
    #                         "leftEmoji": "☕",
    #                         "leftEmojiCodepoint": "2615",
    #                         "rightEmoji": "☕",
    #                         "rightEmojiCodepoint": "2615",
    #                         "date": "20201001",
    #                         "isLatest": true,
    #                         "gBoardOrder": 378
    #                     }
    #                 ]
    #             }
    #         },
    #     }
    def __init__(self):
        self._emojis = {}
        self._load_all()

    def _load_all(self) -> None:
        self._emojis = _load_config(emoji_data.emoji_json) or {}

    def is_supported(self, emoji_code: str) -> bool:
        return emoji_code in self._emojis.get("knownSupportedEmoji", [])

    def get_combination(self, emoji_code1: str, emoji_code2: str) -> Optional[Dict[str, Any]]:
        return self._emojis.get("data", {}).get(emoji_code1, {}).get("combinations", {}).get(emoji_code2, [{}])[0]

    def get_combination_url(self, emoji_code1: str, emoji_code2: str) -> Optional[str]:
        e1 = _get_emoji_hex_str(emoji_code1)
        e2 = _get_emoji_hex_str(emoji_code2)
        if self.is_supported(e1) and self.is_supported(e2):
            combination = self.get_combination(e1, e2)
            return combination.get("gStaticUrl") if combination else None
        unsupported = [e for e in [emoji_code1, emoji_code2] if not self.is_supported(_get_emoji_hex_str(e))]
        if len(unsupported) == 1:
            raise ValueError(f"不支持的emoji:{unsupported[0]}")
        elif len(unsupported) == 2:
            raise ValueError(f"不支持的emoji:{unsupported[0]},{unsupported[1]}")

    def get_random_combination(self) -> Optional[Dict[str, Any]]:
        e1 = random.choice(self._emojis.get("knownSupportedEmoji", []))
        return random.choice(list(
            self._emojis.get("data", {}).get(e1, {}).get("combinations", {}).values()))[0]
