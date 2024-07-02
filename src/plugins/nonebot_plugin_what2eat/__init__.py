from nonebot.plugin import PluginMetadata

__what2eat_version__ = "v0.2.5"
__what2eat_usages__ = f'''
今天吃什么？ {__what2eat_version__}
[xx吃xx]    问bot吃什么
[xx喝xx]    问bot喝什么'''.strip()

__plugin_meta__ = PluginMetadata(
    name="今天吃什么？",
    description="选择恐惧症？让Bot建议你今天吃/喝什么！",
    usage=__what2eat_usages__,
    extra={
        "author": "sugayoiya",
        "version": __what2eat_version__
    }
)

from . import command as command
