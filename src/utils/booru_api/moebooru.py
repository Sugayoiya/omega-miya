"""
@Author         : Ailitonia
@Date           : 2024/8/13 11:17:23
@FileName       : moebooru.py
@Project        : omega-miya
@Description    : Moebooru API (Moebooru 1.13.0-1.13.0+update.3, 兼容 Gelbooru 1.13) (Read requests only)
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

import abc
from typing import TYPE_CHECKING, Any, Literal, Optional

from src.compat import parse_obj_as
from src.utils.common_api import BaseCommonAPI
from .models.moebooru import (
    Post,
    SimilarPosts,
    Tag,
    Artist,
    Comment,
    Wiki,
    Note,
    User,
    Forum,
    Pool,
)

if TYPE_CHECKING:
    from nonebot.internal.driver import CookieTypes, HeaderTypes, QueryTypes


class BaseMoebooruAPI(BaseCommonAPI, abc.ABC):
    """Moebooru API 基类

    文档参考 https://github.com/moebooru/moebooru/blob/master/app/views/help/api.en.html.erb
    端点参考 https://github.com/moebooru/moebooru/blob/master/config/routes.rb
    """

    def __init__(self, *, login_name: Optional[str] = None, password_hash: Optional[str] = None):
        """初始化鉴权信息

        :param login_name: Your login name.
        :param password_hash: Your SHA1 hashed password.
            Simply hashing your plain password will NOT work since Danbooru salts its passwords.
            The actual string that is hashed is "{site_password_salt}--your-password--".
            The "site_password_salt" can be found in "Help:API" page.
        """
        self.__login = login_name
        self.__password_hash = password_hash

    @property
    def _auth_params(self) -> dict[str, str]:
        if self.__login is None or self.__password_hash is None:
            return {}

        return {'login': self.__login, 'password_hash': self.__password_hash}

    @classmethod
    async def _async_get_root_url(cls, *args, **kwargs) -> str:
        return cls._get_root_url(*args, **kwargs)

    @classmethod
    def _get_default_headers(cls) -> "HeaderTypes":
        return {}

    @classmethod
    def _get_default_cookies(cls) -> "CookieTypes":
        return None

    async def get_json(
            self,
            url: str,
            params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """使用 GET 方法请求 API, 返回 json 内容"""
        if isinstance(params, dict):
            params.update(self._auth_params)
        else:
            params = self._auth_params

        return await self._get_json(url, params)

    async def get_resource_as_bytes(
            self,
            url: str,
            params: "QueryTypes" = None,
            *,
            timeout: int = 30,
    ) -> bytes:
        return await self._get_resource_as_bytes(url, params, timeout=timeout)

    async def get_resource_as_text(
            self,
            url: str,
            params: "QueryTypes" = None,
            *,
            timeout: int = 10,
    ) -> str:
        return await self._get_resource_as_text(url, params, timeout=timeout)

    """Posts API"""

    async def posts_index(
            self,
            *,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            tags: Optional[str] = None,
    ) -> list[Post]:
        index_url = f'{self._get_root_url()}/post.json'

        params = {}
        if limit is not None:
            params.update({'limit': str(limit)})
        if page is not None:
            params.update({'page': str(page)})
        if tags is not None:
            params.update({'tags': tags})
        params = None if not params else params

        return parse_obj_as(list[Post], await self.get_json(url=index_url, params=params))

    async def posts_show_popular_by_day(self) -> list[Post]:
        index_url = f'{self._get_root_url()}/post/popular_by_day.json'
        return parse_obj_as(list[Post], await self.get_json(url=index_url))

    async def posts_show_popular_by_month(self) -> list[Post]:
        index_url = f'{self._get_root_url()}/post/popular_by_month.json'
        return parse_obj_as(list[Post], await self.get_json(url=index_url))

    async def posts_show_popular_by_week(self) -> list[Post]:
        index_url = f'{self._get_root_url()}/post/popular_by_week.json'
        return parse_obj_as(list[Post], await self.get_json(url=index_url))

    async def posts_show_popular_recent(self) -> list[Post]:
        index_url = f'{self._get_root_url()}/post/popular_recent.json'
        return parse_obj_as(list[Post], await self.get_json(url=index_url))

    async def post_show(self, id_: int) -> Post:
        """获取 post 信息

        moebooru 没有直接提供根据 ID 获取 Post json 数据的 API, 需使用 `/post.json?tags=id:1234` 查询方法
        参考 https://github.com/moebooru/moebooru/issues/144
        """
        post_list = await self.posts_index(tags=f'id:{id_}')
        if not post_list:
            raise IndexError(f'Post(id={id_}) Not Found')
        return post_list[0]

    async def post_show_similar(self, id_: int) -> SimilarPosts:
        index_url = f'{self._get_root_url()}/post/similar/{id_}.json'
        return SimilarPosts.model_validate(await self.get_json(url=index_url))

    """Tags API"""

    async def tags_index(
            self,
            *,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            order: Optional[Literal['date', 'count', 'name']] = None,
            id_: Optional[int] = None,
            after_id: Optional[int] = None,
            name: Optional[str] = None,
            name_pattern: Optional[str] = None,
    ) -> list[Tag]:
        index_url = f'{self._get_root_url()}/tag.json'

        params = {}
        if limit is not None:
            params.update({'limit': str(limit)})
        if page is not None:
            params.update({'page': str(page)})
        if order is not None:
            params.update({'order': order})
        if id_ is not None:
            params.update({'id': str(id_)})
        if after_id is not None:
            params.update({'after_id': str(after_id)})
        if name is not None:
            params.update({'name': name})
        if name_pattern is not None:
            params.update({'name_pattern': name_pattern})
        params = None if not params else params

        return parse_obj_as(list[Tag], await self.get_json(url=index_url, params=params))

    """Artists API"""

    async def artists_index(
            self,
            *,
            name: Optional[str] = None,
            order: Optional[Literal['date', 'name']] = None,
            page: Optional[int] = None,
    ) -> list[Artist]:
        index_url = f'{self._get_root_url()}/artist.json'

        params = {}
        if name is not None:
            params.update({'name': name})
        if order is not None:
            params.update({'order': order})
        if page is not None:
            params.update({'page': str(page)})
        params = None if not params else params

        return parse_obj_as(list[Artist], await self.get_json(url=index_url, params=params))

    """Comments API"""

    async def comment_show(self, id_: int) -> Comment:
        url = f'{self._get_root_url()}/comment/show.json/{id_}'
        # alternative_url = f'{self._get_root_url()}/comment/show/{id_}.json'

        return Comment.model_validate(await self.get_json(url=url))

    """Wiki API"""

    async def wikis_index(
            self,
            *,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            order: Optional[Literal['title', 'date']] = None,
            query: Optional[str] = None,
    ) -> list[Wiki]:
        index_url = f'{self._get_root_url()}/wiki.json'

        params = {}
        if limit is not None:
            params.update({'limit': str(limit)})
        if page is not None:
            params.update({'page': str(page)})
        if order is not None:
            params.update({'order': order})
        if query is not None:
            params.update({'query': query})
        params = None if not params else params

        return parse_obj_as(list[Wiki], await self.get_json(url=index_url, params=params))

    """Notes API"""

    async def notes_search(self, query: str) -> list[Note]:
        """search notes by query keyword"""
        index_url = f'{self._get_root_url()}/note/search.json'
        params = {'query': query}

        return parse_obj_as(list[Note], await self.get_json(url=index_url, params=params))

    async def note_post_show(self, post_id: int) -> list[Note]:
        """show post's notes"""
        url = f'{self._get_root_url()}/note.json'
        params = {'post_id': post_id}

        return parse_obj_as(list[Note], await self.get_json(url=url, params=params))

    """Users API"""

    async def users_index(
            self,
            *,
            id_: Optional[int] = None,
            name: Optional[str] = None,
    ) -> list[User]:
        index_url = f'{self._get_root_url()}/user.json'

        params = {}
        if id_ is not None:
            params.update({'id': str(id_)})
        if name is not None:
            params.update({'name': name})
        params = None if not params else params

        return parse_obj_as(list[User], await self.get_json(url=index_url, params=params))

    """Forum API"""

    async def forums_index(
            self,
            *,
            parent_id: Optional[int] = None,
    ) -> list[Forum]:
        index_url = f'{self._get_root_url()}/forum.json'
        params = {'parent_id': str(parent_id)} if parent_id is not None else None

        return parse_obj_as(list[Forum], await self.get_json(url=index_url, params=params))

    """Pools API"""

    async def pools_index(
            self,
            *,
            query: Optional[str] = None,
            page: Optional[int] = None,
    ) -> list[Pool]:
        index_url = f'{self._get_root_url()}/pool.json'

        params = {}
        if query is not None:
            params.update({'query': query})
        if page is not None:
            params.update({'page': str(page)})
        params = None if not params else params

        return parse_obj_as(list[Pool], await self.get_json(url=index_url, params=params))

    async def pool_posts_show(self, pool_id: int, *, page: Optional[int] = None) -> Pool:
        url = f'{self._get_root_url()}/pool/show.json'
        # alternative_url = f'{self._get_root_url()}/pool/show/{pool_id}.json'

        params = {'id': str(pool_id)}
        if page is not None:
            params.update({'page': str(page)})

        return Pool.model_validate(await self.get_json(url=url, params=params))


class KonachanAPI(BaseMoebooruAPI):
    """https://konachan.com 主站 API"""

    @classmethod
    def _get_root_url(cls, *args, **kwargs) -> str:
        return 'https://konachan.com'


class YandereAPI(BaseMoebooruAPI):
    """https://yande.re 主站 API"""

    @classmethod
    def _get_root_url(cls, *args, **kwargs) -> str:
        return 'https://yande.re'


__all__ = [
    'KonachanAPI',
    'YandereAPI',
]
