"""
@Author         : Ailitonia
@Date           : 2021/12/24 11:09
@FileName       : roll.py
@Project        : nonebot2_miya
@Description    : 骰子插件
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='群抽奖',
    description='【抽奖插件】\n'
                '抽群友',
    usage='/lottery <num>\n'
          '/抽奖 <num>',
    extra={'author': 'sugayoiya'},
)

from . import command as command

__all__ = []
