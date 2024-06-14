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
    name='Roll',
    description='【骰子插件】\n'
                '各种姿势的掷骰子',
    usage='/roll num\n'
          '/roll d<num>\n'
          '/rd num\n'
          '/rd <num>d<num>',
    extra={'author': 'Ailitonia'},
)


from . import command as command


__all__ = []
