from dataclasses import dataclass

from nonebot import logger
from pydantic import ValidationError

from src.resource import StaticResource


@dataclass
class DrinkReminderLocalResourceConfig:
    """吃什么文件配置"""
    quote: StaticResource = StaticResource('docs', 'drink_reminder', 'quote.json')
    # 默认内置的静态资源文件路径
    groups: StaticResource = StaticResource('docs', 'drink_reminder', 'drinks.json')


try:
    drink_config = DrinkReminderLocalResourceConfig()
except ValidationError as e:
    import sys

    logger.opt(colors=True).critical(f'<r> drink reminder 插件配置格式验证失败</r>, 错误信息:\n{e}')
    sys.exit(f'drink reminder 插件配置格式验证失败, {e}')

__all__ = [
    'drink_config'
]
