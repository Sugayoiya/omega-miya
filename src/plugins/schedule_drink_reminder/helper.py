import random
from typing import Any, Optional
from typing import Dict

import ujson as json
from nonebot import get_bot
from nonebot import logger
from nonebot.adapters.onebot.v11 import ActionFailed
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from src.resource import TemporaryResource
from src.service import OmegaInterface
from .config import drink_config


def _load_config(file: TemporaryResource) -> Optional[Dict[str, Any]]:
    """从文件读取"""
    if file.is_file:
        logger.debug(f'loading fortune event form {file}')
        with file.open('r', encoding='utf8') as f:
            eat_config = json.loads(f.read())
        return eat_config
    else:
        return None


def _save_config(file: TemporaryResource, data: Dict[str, Any]) -> None:
    """保存到文件"""
    with file.open('w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


class DrinkManager:
    def __init__(self):
        self._quote = drink_config.quote
        self._drink_reminder_group = drink_config.groups

        self._drink_reminder_json = _load_config(self._drink_reminder_group)
        self._quote_json = _load_config(self._quote)

    def update_groups_on(self, gid: str, new_state: bool) -> None:
        self._drink_reminder_json = _load_config(self._drink_reminder_group)

        if new_state:
            self._drink_reminder_json["groups_id"].update({gid: True})
        else:
            if gid in self._drink_reminder_json["groups_id"]:
                self._drink_reminder_json["groups_id"].update({gid: False})

        _save_config(self._drink_reminder_group, self._drink_reminder_json)

    async def drink_reminder(self):
        bot = get_bot()
        for gid in self._drink_reminder_json["groups_id"]:
            if self._drink_reminder_json["groups_id"].get(gid, False):
                try:
                    await bot.call_api("send_group_msg", group_id=int(gid),
                                       message=random.choice(list(self._quote_json)))
                    logger.info(f"群 {gid} 发送提醒喝水成功")
                except ActionFailed as e:
                    logger.warning(f"群 {gid} 发送提醒喝水失败：{e}")


drink_manager = DrinkManager()


async def drink_reminder_on(event: GroupMessageEvent):
    gid = str(event.group_id)
    interface = OmegaInterface()
    drink_manager.update_groups_on(gid, True)
    await interface.finish("已开启提醒喝水小助手~")


async def drink_reminder_off(event: GroupMessageEvent):
    gid = str(event.group_id)
    interface = OmegaInterface()
    drink_manager.update_groups_on(gid, False)
    await interface.finish("已关闭提醒喝水小助手~")


__all__ = [
    drink_reminder_on,
    drink_reminder_off,
    drink_manager
]
