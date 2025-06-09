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
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class FileHostConfig(BaseModel):
    """OmegaFileHost 文件托管服务配置"""

    # 启用文件托管服务
    omega_file_host_enable_hosting_service: bool = Field(default=False)
    # 外部访问域名
    omega_file_host_access_domain: str | None = Field(default=None)
    # 返回访问 URL 是是否使用 https
    omega_file_host_use_https: bool = Field(default=False)
    # 文件托管缓存时间
    omega_file_host_cache_ttl: int = Field(default=1800)

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
