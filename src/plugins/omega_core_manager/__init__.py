"""
@Author         : Ailitonia
@Date           : 2023/7/3 2:42
@FileName       : omega_core_manager
@Project        : nonebot2_miya
@Description    : Omega 核心管理插件
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name='botCoreManager',
    description='【bot核心管理插件】\n'
                '机器人开关、维护、功能及权限管理',
    usage='/start  启用/初始化\n'
          '/disable  禁用\n'
          '/status  查看状态\n'
          '/help  帮助\n\n'
          '管理员命令:\n'
          '/bot.set-level [level]\n'
          '/bot.list-commands\n'
          '/bot.list-plugins\n'
          '/bot.enable-plugin [plugin_name]\n'
          '/bot.disable-plugin [plugin_name]\n'
          '/bot.show-plugin-nodes [plugin_name]\n'
          '/bot.allow-plugin-node [plugin_name] [auth_node]\n'
          '/bot.deny-plugin-node [plugin_name] [auth_node]\n'
          '/bot.list-configured-auth\n'
          '/bot.set-limiting [seconds]',
    config=None,
    extra={'author': 'Ailitonia'},
)


from . import command as command


__all__ = []
