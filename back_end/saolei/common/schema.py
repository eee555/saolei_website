from ninja import Schema

from userprofile.schema import SelfUserInfoOut
from videomanager.schema import VideoMetadataOut


class AutoLoginOut(Schema):
    user: SelfUserInfoOut | None
    top_anchors: dict


class AnalyzerRankOut(Schema):
    ranking: str
    stat: str
    nf: bool
    rank: int


class AnalyzerWebsiteInfoOut(Schema):
    video: VideoMetadataOut
    tournament_ids: list[int]
    filename: str
    rankings: list[AnalyzerRankOut]
