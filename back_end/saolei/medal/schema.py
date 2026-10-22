from datetime import date, datetime

from ninja import Schema


class CatalogItemOut(Schema):
    code: str
    series: str
    subseries: str
    kind: str
    metric: str
    direction: str
    level: str
    style: str
    thresholds: list[int]
    hidden: bool
    annotation: str


class MedalItemOut(Schema):
    code: str
    series: str
    subseries: str
    kind: str
    stage: int | None
    stage_count: int
    direction: str
    current_value: int | None
    next_threshold: int | None
    granted_at: datetime | None
    video_id: int | None
    tournament_id: int | None
    rank: int | None
    hidden: bool
    annotation: str
    score: int
    grant_id: int | None
    scope_key: str
    thresholds: list[int]


class SeriesOut(Schema):
    series: str
    items: list[MedalItemOut]


class PlayerMedalOut(Schema):
    score: int
    max_pins: int
    pin_ids: list[int]
    pins: list[MedalItemOut]
    series: list[SeriesOut]


class GrantPageOut(Schema):
    count: int
    page: int
    page_size: int
    items: list[MedalItemOut]


class PinsIn(Schema):
    grant_ids: list[int]


class PinsOut(Schema):
    pin_ids: list[int]


class StaffGrantIn(Schema):
    code: str
    user_id: int
    reason: str
    granted_on: date


class GrantIdOut(Schema):
    id: int


class RevokeIn(Schema):
    reason: str


class RebuildIn(Schema):
    user_id: int


class EnqueuedOut(Schema):
    enqueued: bool
