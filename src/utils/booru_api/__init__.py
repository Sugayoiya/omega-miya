"""
@Author         : Ailitonia
@Date           : 2024/8/1 14:45:35
@FileName       : booru_api.py
@Project        : omega-miya
@Description    : Danbooru 及其衍生 API (Read requests only)
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from .config import booru_config as booru_config
from .danbooru import DanbooruAPI
from .gelbooru import GelbooruAPI


danbooru_api = DanbooruAPI(username=booru_config.danbooru_username, api_key=booru_config.danbooru_api_key)
gelbooru_api = GelbooruAPI(user_id=booru_config.gelbooru_user_id, api_key=booru_config.gelbooru_api_key)


__all__ = [
    'danbooru_api',
    'gelbooru_api',
]
