"""
@Author         : Ailitonia
@Date           : 2022/04/05 22:03
@FileName       : model.py
@Project        : nonebot2_miya 
@Description    : Pixiv Model
@GitHub         : https://github.com/Ailitonia
@Software       : PyCharm 
"""

from .artwork import (PixivArtworkDataModel, PixivArtworkPageModel, PixivArtworkUgoiraMeta,
                      PixivArtworkCompleteDataModel, PixivArtworkRecommendModel,
                      PixivArtworkPreviewRequestModel)
from .ranking import PixivRankingModel
from .searching import PixivSearchingResultModel
from .discovery import PixivDiscoveryModel, PixivRecommendModel
from .user import (PixivGlobalData, PixivUserDataModel, PixivUserArtworkDataModel, PixivUserModel,
                   PixivUserSearchingModel, PixivFollowLatestIllust, PixivBookmark)
from .pixivision import PixivisionArticle, PixivisionIllustrationList


__all__ = [
    'PixivArtworkDataModel',
    'PixivArtworkPageModel',
    'PixivArtworkUgoiraMeta',
    'PixivArtworkCompleteDataModel',
    'PixivArtworkRecommendModel',
    'PixivArtworkPreviewRequestModel',
    'PixivRankingModel',
    'PixivSearchingResultModel',
    'PixivDiscoveryModel',
    'PixivRecommendModel',
    'PixivGlobalData',
    'PixivUserDataModel',
    'PixivUserArtworkDataModel',
    'PixivUserModel',
    'PixivUserSearchingModel',
    'PixivFollowLatestIllust',
    'PixivisionArticle',
    'PixivisionIllustrationList',
    'PixivBookmark'
]
