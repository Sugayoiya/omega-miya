"""
@Author         : Ailitonia
@Date           : 2022/12/04 16:59
@FileName       : subscription_source.py
@Project        : nonebot2_miya 
@Description    : SubscriptionSource DAL
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from copy import deepcopy
from datetime import datetime
from enum import Enum, unique
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import Literal, Optional

from pydantic import BaseModel, parse_obj_as

from ..model import BaseDataAccessLayerModel, SubscriptionSourceOrm


@unique
class SubscriptionSourceType(Enum):
    """订阅源 类型"""
    bili_live: Literal['bili_live'] = 'bili_live'
    bili_dynamic: Literal['bili_dynamic'] = 'bili_dynamic'
    pixiv_user: Literal['pixiv_user'] = 'pixiv_user'
    pixivision: Literal['pixivision'] = 'pixivision'

    @classmethod
    def verify(cls, unverified: str):
        if unverified not in [member.value for _, member in cls.__members__.items()]:
            raise ValueError(f'illegal subscription_source_type: "{unverified}"')


class SubscriptionSource(BaseModel):
    """订阅源 Model"""
    id: int
    sub_type: str
    sub_id: str
    sub_user_name: str
    sub_info: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        extra = 'ignore'
        orm_mode = True
        allow_mutation = False


class SubscriptionSourceDAL(BaseDataAccessLayerModel):
    """订阅源 数据库操作对象"""

    def __init__(self, session: AsyncSession):
        self.db_session = session

    @property
    def subscription_source_type(self) -> type[SubscriptionSourceType]:
        return deepcopy(SubscriptionSourceType)

    async def query_unique(self, sub_type: str, sub_id: str) -> SubscriptionSource:
        stmt = select(SubscriptionSourceOrm).\
            where(SubscriptionSourceOrm.sub_type == sub_type).\
            where(SubscriptionSourceOrm.sub_id == sub_id)
        session_result = await self.db_session.execute(stmt)
        return SubscriptionSource.from_orm(session_result.scalar_one())

    async def query_all(self) -> list[SubscriptionSource]:
        stmt = select(SubscriptionSourceOrm).order_by(SubscriptionSourceOrm.sub_type)
        session_result = await self.db_session.execute(stmt)
        return parse_obj_as(list[SubscriptionSource], session_result.scalars().all())

    async def add(self, sub_type: str, sub_id: str, sub_user_name: str, sub_info: Optional[str] = None) -> None:
        SubscriptionSourceType.verify(sub_type)
        new_obj = SubscriptionSourceOrm(sub_type=sub_type, sub_id=sub_id, sub_user_name=sub_user_name,
                                        sub_info=sub_info, created_at=datetime.now())
        self.db_session.add(new_obj)
        await self.db_session.flush()

    async def update(
            self,
            id_: int,
            *,
            sub_type: Optional[str] = None,
            sub_id: Optional[str] = None,
            sub_user_name: Optional[str] = None,
            sub_info: Optional[str] = None
    ) -> None:
        stmt = update(SubscriptionSourceOrm).where(SubscriptionSourceOrm.id == id_)
        if sub_type is not None:
            SubscriptionSourceType.verify(sub_type)
            stmt = stmt.values(sub_type=sub_type)
        if sub_id is not None:
            stmt = stmt.values(sub_id=sub_id)
        if sub_user_name is not None:
            stmt = stmt.values(sub_user_name=sub_user_name)
        if sub_info is not None:
            stmt = stmt.values(sub_info=sub_info)
        stmt = stmt.values(updated_at=datetime.now())
        stmt.execution_options(synchronize_session="fetch")
        await self.db_session.execute(stmt)

    async def delete(self, id_: int) -> None:
        stmt = delete(SubscriptionSourceOrm).where(SubscriptionSourceOrm.id == id_)
        stmt.execution_options(synchronize_session="fetch")
        await self.db_session.execute(stmt)


__all__ = [
    'SubscriptionSourceDAL'
]
