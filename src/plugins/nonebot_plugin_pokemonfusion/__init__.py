from nonebot.plugin import PluginMetadata

__pokemon_fusion_version__ = "v0.2.5"
__pokemon_fusion_usages__ = f'''
宝可梦融合! {__pokemon_fusion_version__}
/融合 宝可梦1+宝可梦2
/宝可梦融合 宝可梦1+宝可梦2'''.strip()

__plugin_meta__ = PluginMetadata(
    name="宝可梦融合",
    description="宝可梦融合!",
    usage=__pokemon_fusion_usages__,
    extra={
        "author": "sugayoiya",
        "version": __pokemon_fusion_version__
    }
)

from . import command as command
