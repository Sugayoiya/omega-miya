from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='llm聊天bot',
    description="具有上下文关联和多模态识别(todo)，适配OneAPI和OpenAI官方的nonebot插件。",
    usage="""
    @bot发送问题时机器人不具有上下文回复的能力，tokens消耗较少，2s CD
    /chat 使用该命令进行问答时，bot具有上下文回复的能力，比较消耗tokens，暂定5s CD
    /clear 清除当前的群-用户上下文
    /gchat 群接龙
    /gclear 清楚群接龙上下文
    """,
    extra={'author': 'sugayoiya'},
)

from . import command as command

__all__ = []
