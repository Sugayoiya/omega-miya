from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='emoji合成',
    description='【emoji合成】\n'
                '😀+😀=?',
    usage='直接发送 emoji+emoji 即可',
    extra={'author': 'sugayoiya'},
)

from . import command as command

__all__ = []
