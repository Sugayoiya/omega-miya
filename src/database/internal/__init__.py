"""
@Author         : Ailitonia
@Date           : 2022/12/01 20:49
@FileName       : internal.py
@Project        : nonebot2_miya
@Description    : Data access layer model
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm
"""

from typing import Annotated

from nonebot.params import Depends

from .artwork_collection import ArtworkCollectionDAL
from .auth_setting import AuthSettingDAL
from .bot import BotSelfDAL
from .cooldown import CoolDownDAL
from .entity import EntityDAL
from .friendship import FriendshipDAL
from .global_cache import GlobalCacheDAL
from .history import HistoryDAL
from .plugin import PluginDAL
from .sign_in import SignInDAL
from .social_media_content import SocialMediaContentDAL
from .statistic import StatisticDAL
from .subscription import SubscriptionDAL
from .subscription_source import SubscriptionSourceDAL
from .system_setting import SystemSettingDAL
from .word_bank import WordBankDAL

type ARTWORK_COLLECTION_DAL = Annotated[ArtworkCollectionDAL, Depends(ArtworkCollectionDAL.dal_dependence)]
"""子依赖: 获取 ArtworkCollectionDAL 并开始事务"""
type AUTH_SETTING_DAL = Annotated[AuthSettingDAL, Depends(AuthSettingDAL.dal_dependence)]
"""子依赖: 获取 AuthSettingDAL 并开始事务"""
type BOT_SELF_DAL = Annotated[BotSelfDAL, Depends(BotSelfDAL.dal_dependence)]
"""子依赖: 获取 BotSelfDAL 并开始事务"""
type COOL_DOWN_DAL = Annotated[CoolDownDAL, Depends(CoolDownDAL.dal_dependence)]
"""子依赖: 获取 CoolDownDAL 并开始事务"""
type ENTITY_DAL = Annotated[EntityDAL, Depends(EntityDAL.dal_dependence)]
"""子依赖: 获取 EntityDAL 并开始事务"""
type FRIENDSHIP_DAL = Annotated[FriendshipDAL, Depends(FriendshipDAL.dal_dependence)]
"""子依赖: 获取 FriendshipDAL 并开始事务"""
type GLOBAL_CACHE_DAL = Annotated[GlobalCacheDAL, Depends(GlobalCacheDAL.dal_dependence)]
"""子依赖: 获取 GlobalCacheDAL 并开始事务"""
type HISTORY_DAL = Annotated[HistoryDAL, Depends(HistoryDAL.dal_dependence)]
"""子依赖: 获取 HistoryDAL 并开始事务"""
type PLUGIN_DAL = Annotated[PluginDAL, Depends(PluginDAL.dal_dependence)]
"""子依赖: 获取 PluginDAL 并开始事务"""
type SIGN_IN_DAL = Annotated[SignInDAL, Depends(SignInDAL.dal_dependence)]
"""子依赖: 获取 SignInDAL 并开始事务"""
type SOCIAL_MEDIA_CONTENT_DAL = Annotated[SocialMediaContentDAL, Depends(SocialMediaContentDAL.dal_dependence)]
"""子依赖: 获取 SocialMediaContentDAL 并开始事务"""
type STATISTIC_DAL = Annotated[StatisticDAL, Depends(StatisticDAL.dal_dependence)]
"""子依赖: 获取 StatisticDAL 并开始事务"""
type SUBSCRIPTION_DAL = Annotated[SubscriptionDAL, Depends(SubscriptionDAL.dal_dependence)]
"""子依赖: 获取 SubscriptionDAL 并开始事务"""
type SUBSCRIPTION_SOURCE_DAL = Annotated[SubscriptionSourceDAL, Depends(SubscriptionSourceDAL.dal_dependence)]
"""子依赖: 获取 SubscriptionSourceDAL 并开始事务"""
type SYSTEM_SETTING_DAL = Annotated[SystemSettingDAL, Depends(SystemSettingDAL.dal_dependence)]
"""子依赖: 获取 SystemSettingDAL 并开始事务"""
type WORD_BANK_DAL = Annotated[WordBankDAL, Depends(WordBankDAL.dal_dependence)]
"""子依赖: 获取 WordBankDAL 并开始事务"""


__all__ = [
    'ARTWORK_COLLECTION_DAL',
    'AUTH_SETTING_DAL',
    'BOT_SELF_DAL',
    'COOL_DOWN_DAL',
    'ENTITY_DAL',
    'FRIENDSHIP_DAL',
    'GLOBAL_CACHE_DAL',
    'HISTORY_DAL',
    'PLUGIN_DAL',
    'SIGN_IN_DAL',
    'SOCIAL_MEDIA_CONTENT_DAL',
    'STATISTIC_DAL',
    'SUBSCRIPTION_DAL',
    'SUBSCRIPTION_SOURCE_DAL',
    'SYSTEM_SETTING_DAL',
    'WORD_BANK_DAL',
    'ArtworkCollectionDAL',
    'AuthSettingDAL',
    'BotSelfDAL',
    'CoolDownDAL',
    'EntityDAL',
    'FriendshipDAL',
    'GlobalCacheDAL',
    'HistoryDAL',
    'PluginDAL',
    'SignInDAL',
    'SocialMediaContentDAL',
    'StatisticDAL',
    'SubscriptionDAL',
    'SubscriptionSourceDAL',
    'SystemSettingDAL',
    'WordBankDAL',
]
