from nonebot.plugin import PluginMetadata

from .helper import eating_manager

__what2eat_version__ = "v0.2.5"
__what2eat_usages__ = f'''
今天吃什么？ {__what2eat_version__}
[xx吃xx]    问bot吃什么
[xx喝xx]    问bot喝什么
[添加 xx]   添加菜品至群菜单
[移除 xx]   从菜单移除菜品
[加菜 xx]   添加菜品至基础菜单
[菜单]        查看群菜单
[基础菜单] 查看基础菜单
[开启/关闭小助手] 开启/关闭吃饭小助手
[添加/删除问候 时段 问候语] 添加/删除吃饭小助手问候语'''.strip()

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
