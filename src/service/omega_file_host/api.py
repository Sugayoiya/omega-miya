"""
@Author         : Ailitonia
@Date           : 2025/5/30 11:12:41
@FileName       : api.py
@Project        : omega-miya
@Description    : 文件托管服务 API
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from fastapi import HTTPException
from fastapi.responses import FileResponse

from src.resource import AnyResource, BaseResource
from src.service.omega_api import OmegaAPI
from .config import file_host_config
from .utils import query_file_path, query_file_uuid

_FILE_HOST_API = OmegaAPI(
    app_name='omega_file_host',
    access_domain=file_host_config.omega_file_host_access_domain,
    use_https=file_host_config.omega_file_host_use_https,
)
"""文件服务 API"""

if file_host_config.omega_file_host_enable_hosting_service:
    @_FILE_HOST_API.register_get_route('/download/{file_id}')
    async def _download_file(file_id: str) -> FileResponse:
        file_path = await query_file_path(file_id)

        if not file_path:
            raise HTTPException(status_code=404, detail="File expired or deleted")

        file = AnyResource(file_path)
        if not file.is_file:
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file.path,
            filename=f'{file_id}{file.path.suffix}',
            media_type='application/octet-stream',
        )


async def get_hosting_file_path(file: 'BaseResource') -> str:
    """获取文件路径, 启用文件服务 API 时返回下载 URL, 未启用时返回文件本地路径"""
    if file_host_config.omega_file_host_enable_hosting_service:
        file_uuid = await query_file_uuid(file)
        return f'{_FILE_HOST_API.root_url}/download/{file_uuid}'
    else:
        return file.resolve_path


__all__ = [
    'get_hosting_file_path',
]
