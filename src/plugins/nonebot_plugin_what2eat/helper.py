import random
from typing import Any, List, Optional
from typing import Dict, Tuple

import ujson as json
from nonebot import logger

from src.resource import TemporaryResource
from src.service import OmegaInterface
from src.service import OmegaRequests
from .config import eat_config, eat_local_resource_config


async def download_resource_url(name: str) -> Optional[Dict[str, Any]]:
    url: str = "https://raw.githubusercontent.com/Sugayoiya/omega-miya/dev/static/docs/what_eat/" + name

    response = await OmegaRequests(timeout=30).get(url)
    if response.status_code != 200:
        logger.warning(f"Error occured when downloading {url}")
        return None
    return OmegaRequests.parse_content_json(response)


def _load_config(file: TemporaryResource) -> Optional[Dict[str, Any]]:
    """从文件读取求签事件"""
    if file.is_file:
        logger.debug(f'loading fortune event form {file}')
        with file.open('r', encoding='utf8') as f:
            eat_config = json.loads(f.read())
        return eat_config
    else:
        return None


def _save_config(file: TemporaryResource, data: Dict[str, Any]) -> None:
    """保存求签事件到文件"""
    with file.open('w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))


def _update_config(file: TemporaryResource, data: Dict[str, Any]) -> None:
    """更新求签事件到文件"""
    if file.is_file:
        logger.debug(f'updating fortune event form {file}')
        with file.open('w', encoding='utf8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
    else:
        _save_config(file, data)


class EatingManager:
    def __init__(self):
        self._dishes = {}
        self._drinks = {}
        self._greetings = {}
        self._load_all()

    def _load_all(self) -> None:
        self._dishes = _load_config(eat_local_resource_config.dishes) or {}
        self._drinks = _load_config(eat_local_resource_config.drinks) or {}
        self._greetings = _load_config(eat_local_resource_config.greetings) or {}

    def get_percentage_item_str(self, item: List[str]) -> str:
        select_food_list = random.choices(item, k=eat_config.eating_sample_count)
        percent = [random.randint(1, 99) for _ in range(eat_config.eating_sample_count)]
        percent_int = [int(i / sum(percent) * 100) for i in percent[:-1]]
        percent_int.append(100 - sum(percent_int))
        choice_list = []
        for i in list(zip(select_food_list, percent_int)):
            choice_list.append(i[0] + " " + str(i[1]) + "%")
        return "\n".join(choice_list)

    def get2eat(self) -> str:
        return "建议 " + self.get_percentage_item_str(self._dishes["basic_food"])

    def get2drink(self) -> str:
        # _branch, _drink = self.pick_one_drink()
        return self.get_percentage_drinks_str()

    def pick_one_drink(self) -> Tuple[str, str]:
        _drinks: Dict[str, List[str]] = self._drinks
        _branch: str = random.choice(list(_drinks))
        _drink: str = random.choice(_drinks[_branch])

        return _branch, _drink

    def get_percentage_drinks_str(self) -> str:
        _drinks: Dict[str, List[str]] = self._drinks
        select_drink_list = []
        for i in range(eat_config.eating_sample_count):
            _branch: str = random.choice(list(_drinks))
            _drink: str = random.choice(_drinks[_branch])
            select_drink_list.append("「" + _branch + "」的「" + _drink + "」")
        percent = [random.randint(1, 99) for _ in range(eat_config.eating_sample_count)]
        percent_int = [int(i / sum(percent) * 100) for i in percent[:-1]]
        percent_int.append(100 - sum(percent_int))
        choice_list = []
        for i in list(zip(select_drink_list, percent_int)):
            choice_list.append(i[0] + " " + str(i[1]) + "%")

        return "建议 " + "\n ".join(choice_list)


eating_manager = EatingManager()


async def what2eat():
    interface = OmegaInterface()
    msg = eating_manager.get2eat()
    await interface.finish(msg)


async def what2drink():
    interface = OmegaInterface()
    msg = eating_manager.get2drink()
    await interface.finish(msg)


__all__ = [
    eating_manager,
    what2eat,
    what2drink
]
