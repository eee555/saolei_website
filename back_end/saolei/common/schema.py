from django.db import models
from ninja import Schema
from ninja.orm import create_schema

from userprofile.schema import SelfUserInfoOut
from videomanager.models import ExpandVideoModel, VideoModel


class AutoLoginOut(Schema):
    user: SelfUserInfoOut | None
    top_anchors: dict


AnalyzerVideoOut = create_schema(
    VideoModel,
    name='AnalyzerVideoOut',
    fields=[field.name for field in VideoModel._meta.fields],
    custom_fields=[
        (field.name, float | None if isinstance(field.output_field, models.FloatField) else int | None, None)
        for field in VideoModel._meta.fields if isinstance(field, models.GeneratedField)
    ],
)
AnalyzerExpandedVideoOut = create_schema(
    ExpandVideoModel,
    name='AnalyzerExpandedVideoOut',
    fields=[field.name for field in ExpandVideoModel._meta.fields],
)


class AnalyzerRankOut(Schema):
    ranking: str
    stat: str
    nf: bool
    rank: int


class AnalyzerWebsiteInfoOut(Schema):
    video: AnalyzerVideoOut
    expanded_video: AnalyzerExpandedVideoOut
    tournament_ids: list[int]
    filename: str
    rankings: list[AnalyzerRankOut]
