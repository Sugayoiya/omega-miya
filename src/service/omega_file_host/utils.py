"""
@Author         : Ailitonia
@Date           : 2025/5/30 11:31:11
@FileName       : utils.py
@Project        : omega-miya
@Description    : 文件缓存及路径处理工具
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

import uuid
from typing import TYPE_CHECKING

from nonebot import get_driver, logger

from src.service.apscheduler import scheduler
from src.service.omega_global_cache import OmegaGlobalCache

if TYPE_CHECKING:
    from src.resource import BaseResource

_FILE_HOST_CACHE: OmegaGlobalCache = OmegaGlobalCache('omega_file_host')


@scheduler.scheduled_job(
    'cron',
    hour='*/2',
    minute='11',
    second='11',
    id='omega_file_host_sync_cache',
    coalesce=True,
)
@get_driver().on_startup
async def _sync_filehost_cache() -> None:
    """同步文件缓存"""
    try:
        await _FILE_HOST_CACHE.sync_internal()
        logger.opt(colors=True).success('<lc>OmegaFileHost</lc> | <lg>文件缓存同步成功</lg>')
    except Exception as e:
        logger.opt(colors=True).error(f'<lc>OmegaFileHost</lc> | <r>文件缓存同步失败</r>, {e}')


async def query_file_uuid(file: 'BaseResource') -> str:
    """获取文件 UUID"""
    file_uuid = uuid.uuid5(namespace=uuid.NAMESPACE_URL, name=file.resolve_path)
    await _FILE_HOST_CACHE.save(file_uuid.hex, file.resolve_path)
    return file_uuid.hex


async def query_file_path(file_uuid: str) -> str | None:
    """根据 UUID 获取文件路径"""
    return await _FILE_HOST_CACHE.load(file_uuid)


__all__ = [
    'query_file_path',
    'query_file_uuid',
]
