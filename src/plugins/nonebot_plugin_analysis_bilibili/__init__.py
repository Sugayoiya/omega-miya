from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="analysis_bilibili",
    description="自动解析bilibili链接内容",
    usage="",
    extra={'author': 'sugayoiya'},
)

from . import command as command

__all__ = []
