"""
@Author         : Ailitonia
@Date           : 2025/6/3 16:08:32
@FileName       : manager.py
@Project        : omega-miya
@Description    : 订阅源管理类
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

import abc
from collections.abc import AsyncGenerator, Iterable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from nonebot.exception import ActionFailed
from nonebot.log import logger

from src.database import SocialMediaContentDAL, begin_db_session
from src.service import (
    OmegaEntity,
    OmegaEntityInterface as OmEI,
    OmegaMatcherInterface as OmMI,
    OmegaMessage,
)
from src.utils import semaphore_gather

if TYPE_CHECKING:
    from src.database.internal.entity import Entity
    from src.database.internal.social_media_content import SocialMediaContent
    from src.database.internal.subscription_source import SubscriptionSource
    from src.service.omega_base.internal.subscription_source import BaseInternalSubscriptionSource


class BaseSubscriptionManager[SMC_T: Any](abc.ABC):
    """订阅服务管理基类"""

    __slots__ = ('sub_id',)
    sub_id: str

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(sub_id={self.sub_id})'

    def __str__(self) -> str:
        return f'{self.__class__.__name__} | {self.sub_type} | {self.sub_id}'

    @classmethod
    @abc.abstractmethod
    def get_subscription_source(cls) -> type['BaseInternalSubscriptionSource']:
        """获取订阅源操作对象"""
        raise NotImplementedError

    @classmethod
    def get_sub_type(cls) -> str:
        """获取订阅源类型"""
        return cls.get_subscription_source().get_sub_type()

    @property
    def sub_source(self) -> type['BaseInternalSubscriptionSource']:
        """获取订阅源操作对象"""
        return self.get_subscription_source()

    @property
    def sub_type(self) -> str:
        """获取订阅源类型"""
        return self.get_sub_type()

    @abc.abstractmethod
    def _gen_sub_source_init_params(self) -> dict[str, Any]:
        """生成订阅源初始化参数"""
        raise NotImplementedError

    @asynccontextmanager
    async def _begin_sub_source_session(self) -> AsyncGenerator['BaseInternalSubscriptionSource', None]:
        """开始订阅源操作对象的会话"""
        async with begin_db_session() as session:
            source = self.sub_source(session=session, **self._gen_sub_source_init_params())
            yield source

    """订阅源内容管理部分"""

    @staticmethod
    @abc.abstractmethod
    def get_smc_item_mid(smc_item: 'SMC_T') -> str:
        """获取订阅源内容对应的 SocialMediaContent mid"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def parse_smc_item(cls, smc_item: 'SMC_T') -> 'SocialMediaContent':
        """将订阅源内容转换为 SocialMediaContent 数据"""
        raise NotImplementedError

    @classmethod
    async def _check_new_smc_item(cls, smc_items: 'Iterable[SMC_T]') -> 'list[SMC_T]':
        """根据 SocialMediaContent mid 检查新的订阅源内容(数据库中没有的)"""
        async with begin_db_session() as session:
            all_mids = [cls.get_smc_item_mid(x) for x in smc_items]
            new_mids = await SocialMediaContentDAL(session=session).query_source_not_exists_mids(
                source=cls.get_sub_type(),
                mids=all_mids,
            )
        return [x for x in smc_items if cls.get_smc_item_mid(x) in new_mids]

    @abc.abstractmethod
    async def _query_sub_source_smc_items(self) -> 'list[SMC_T]':
        """获取订阅源现有的所有内容"""
        raise NotImplementedError

    async def _query_sub_source_new_smc_items(self) -> 'list[SMC_T]':
        """获取订阅源现有的更新内容"""
        all_smc_items = await self._query_sub_source_smc_items()
        return await self._check_new_smc_item(smc_items=all_smc_items)

    @classmethod
    async def _add_upgrade_smc_item(cls, smc_item: 'SMC_T') -> None:
        """在数据库中添加订阅源对应 SocialMediaContent 内容"""
        parsed_smc_item = cls.parse_smc_item(smc_item)
        async with begin_db_session() as session:
            await SocialMediaContentDAL(session=session).upsert(
                source=cls.get_sub_type(),
                m_id=parsed_smc_item.m_id,
                m_type=parsed_smc_item.m_type,
                m_uid=parsed_smc_item.m_uid,
                title=parsed_smc_item.title,
                content=parsed_smc_item.content,
                ref_content=parsed_smc_item.ref_content,
            )

    async def _add_sub_source_new_smc_content(self) -> None:
        """在数据库中更新订阅源的所有新内容(仅新增不更新)"""
        new_smc_items = await self._query_sub_source_new_smc_items()
        tasks = [self._add_upgrade_smc_item(smc_item=smc_item) for smc_item in new_smc_items]
        await semaphore_gather(tasks=tasks, semaphore_num=8, return_exceptions=False)

    """Entity 对象订阅管理部分"""

    @abc.abstractmethod
    async def _query_sub_source_data(self) -> 'SubscriptionSource':
        """从订阅源站点或 API 获取订阅源信息(注意: 本方法返回的订阅源信息索引 ID 为缺省值 -1)"""
        raise NotImplementedError

    async def _query_sub_source(self) -> 'SubscriptionSource':
        """从数据库查询订阅源"""
        async with self._begin_sub_source_session() as source:
            source_res = await source.query_subscription_source()
        return source_res

    async def _add_upgrade_sub_source(self) -> 'SubscriptionSource':
        """在数据库中新更新订阅源"""
        sub_source_data = await self._query_sub_source_data()

        # 提前添加订阅源内容到数据库避免后续检查时将添加时已存在的的内容一并带出
        await self._add_sub_source_new_smc_content()

        # 将订阅源信息写入数据库
        async with self._begin_sub_source_session() as source:
            await source.add_upgrade(sub_user_name=sub_source_data.sub_user_name, sub_info=sub_source_data.sub_info)
            # `self._query_sub_source_data()` 提供的订阅源信息索引 ID 为缺省值, 这里需要反查获取真实的索引 ID
            source_res = await source.query_subscription_source()
        return source_res

    async def add_entity_sub(self, interface: 'OmMI') -> None:
        """为目标 Entity 添加订阅源的对应订阅"""
        source_res = await self._add_upgrade_sub_source()
        await interface.entity.add_subscription(
            subscription_source=source_res,
            sub_info=f'订阅类型: {source_res!r}, 订阅ID: {source_res.sub_id})',
        )

    async def delete_entity_sub(self, interface: 'OmMI') -> None:
        """为目标 Entity 删除订阅源的对应订阅"""
        source_res = await self._add_upgrade_sub_source()
        await interface.entity.delete_subscription(subscription_source=source_res)

    @classmethod
    async def query_entity_subscribed_sub_source(cls, interface: 'OmMI') -> dict[str, str]:
        """获取目标对象已订阅的订阅源

        :return: {sub_id: sub_user_name} 的字典"""
        subscribed_source = await interface.entity.query_subscribed_source(sub_type=cls.get_sub_type())
        return {x.sub_id: x.sub_user_name for x in subscribed_source}

    @classmethod
    async def query_all_subscribed_sub_source_ids(cls) -> list[str]:
        """获取所有已被订阅的订阅源的订阅 ID 列表

        :return: sub_id 列表
        """
        async with begin_db_session() as session:
            source_res = await cls.get_subscription_source().query_type_all(session=session)
        return [x.sub_id for x in source_res]

    async def query_subscribed_entity_by_sub_source(self) -> list['Entity']:
        """根据订阅源查询已经订阅了该订阅源的 Entity 对象"""
        async with self._begin_sub_source_session() as source:
            subscribed_entity = await source.query_all_entity_subscribed()
        return subscribed_entity

    """消息处理和发送管理部分"""

    @staticmethod
    @abc.abstractmethod
    async def _format_smc_item_message(smc_item: 'SMC_T') -> str | OmegaMessage:
        """处理订阅源内容为消息"""
        raise NotImplementedError

    async def _sender_entity_message(self, entity: 'Entity', message: str | OmegaMessage) -> None:
        """向 Entity 发送消息"""
        try:
            async with begin_db_session() as session:
                internal_entity = await OmegaEntity.init_from_entity_index_id(session=session, index_id=entity.id)
                interface = OmEI(entity=internal_entity)
                await interface.send_entity_message(message=message)
        except ActionFailed as e:
            logger.warning(f'{self} | Sending message to {entity} failed with ActionFailed, {e!r}')
        except Exception as e:
            logger.error(f'{self} | Sending message to {entity} failed, {e!r}')

    async def send_subscribed_entity_smc_message(self, smc_item: 'SMC_T') -> None:
        """向所有订阅了该订阅源的 Entity 订阅者发送新订阅内容信息"""
        send_message = await self._format_smc_item_message(smc_item=smc_item)
        subscribed_entity = await self.query_subscribed_entity_by_sub_source()
        send_tasks = [
            self._sender_entity_message(entity=entity, message=send_message)
            for entity in subscribed_entity
        ]
        await semaphore_gather(tasks=send_tasks, semaphore_num=2)


__all__ = [
    'BaseSubscriptionManager',
]
