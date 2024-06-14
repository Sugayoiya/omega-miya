from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='抽象话',
    description='【抽象话】\n'
                '文字转emoji',
    usage='/抽象话 [文字]',
    extra={'author': 'sugayoiya'},
)

from . import command as command

__all__ = []
