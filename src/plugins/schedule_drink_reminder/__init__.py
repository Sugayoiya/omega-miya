from nonebot.plugin import PluginMetadata

from .helper import drink_manager

__drink_reminder__ = "v0.0.1"
__drink_reminder__ = f'''
群喝水提醒小助手？ {__drink_reminder__}
[开启喝水小助手]    开启群喝水小助手
[关闭喝水小助手]    关闭群喝水小助手'''.strip()

__plugin_meta__ = PluginMetadata(
    name='drink_reminder',
    description='提醒喝水小助手',
    usage=f'{__drink_reminder__}',
    extra={'author': 'sugayoiya'},
)

from . import command as command
from . import scheduler as scheduler

__all__ = []
