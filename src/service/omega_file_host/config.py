"""
@Author         : Ailitonia
@Date           : 2025/5/30 17:02:04
@FileName       : config.py
@Project        : omega-miya
@Description    : 文件托管服务配置
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from nonebot import get_plugin_config, logger
from pydantic import BaseModel, ConfigDict, ValidationError


class FileHostConfig(BaseModel):
    # 启用文件托管服务
    omega_file_host_enable_hosting_service: bool = False

    model_config = ConfigDict(extra='ignore')


try:
    file_host_config = get_plugin_config(FileHostConfig)
except ValidationError as e:
    import sys

    logger.opt(colors=True).critical(f'<r>OmegaFileHost 配置格式验证失败</r>, 错误信息:\n{e}')
    sys.exit(f'OmegaFileHost 配置格式验证失败, {e}')

__all__ = [
    'file_host_config',
]
