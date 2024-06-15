from dataclasses import dataclass

from nonebot import get_plugin_config, logger
from pydantic import BaseModel, ConfigDict, ValidationError

from src.resource import StaticResource


class EatConfig(BaseModel):
    # 是否启用正则匹配matcher
    # 如果 bot 配置了命令前缀, 但需要额外响应无前缀的 "签到" 等消息, 请将本选项设置为 True
    # 如果 bot 没有配置命令前缀或空白前缀, 请将本选项设置为 False, 避免重复响应
    eat_enable_regex_matcher: bool = True

    # 吃什么样本数量
    eating_sample_count: int = 5

    model_config = ConfigDict(extra="ignore")


@dataclass
class EatLocalResourceConfig:
    """吃什么文件配置"""

    # 默认内置的静态资源文件路径
    drinks: StaticResource = StaticResource('docs', 'what_eat', 'drinks.json')
    dishes: StaticResource = StaticResource('docs', 'what_eat', 'eating.json')
    greetings: StaticResource = StaticResource('docs', 'what_eat', 'greetings.json')


try:
    eat_local_resource_config = EatLocalResourceConfig()
    eat_config = get_plugin_config(EatConfig)
except ValidationError as e:
    import sys

    logger.opt(colors=True).critical(f'<r> eat 插件配置格式验证失败</r>, 错误信息:\n{e}')
    sys.exit(f'eat 插件配置格式验证失败, {e}')

__all__ = [
    'eat_config',
    'eat_local_resource_config'
]
