from dataclasses import dataclass
from typing import Literal

from config.global_settings import GameLevels
from config.text_choices import MS_TextChoices

LEVELS = GameLevels
MODES = [MS_TextChoices.Mode.STD, MS_TextChoices.Mode.NF, MS_TextChoices.Mode.JSW, MS_TextChoices.Mode.BZD]
RankingStat = Literal['timems', 'bvs', 'stnb', 'ioe', 'path']
RankingMode = Literal['std', 'nf', 'ng', 'dg']
RankingVideoMode = Literal['00', '05', '11', '12']
RankingLevel = Literal['b', 'i', 'e']

VIDEO_RECORD_STATS: tuple[RankingStat, ...] = ('timems', 'bvs', 'stnb', 'ioe', 'path')
VIDEO_MODE_TO_RECORD_MODES: dict[str, tuple[RankingMode, ...]] = {
    MS_TextChoices.Mode.STD: ('std',),
    MS_TextChoices.Mode.NF: ('std', 'nf'),
    MS_TextChoices.Mode.JSW: ('ng',),
    MS_TextChoices.Mode.BZD: ('dg',),
}


@dataclass(frozen=True)
class RankingCategory:
    player_id: int
    level: RankingLevel
    mode: RankingVideoMode


@dataclass(frozen=True)
class RankingField:
    level: RankingLevel
    stat: RankingStat
    mode: RankingMode

    @property
    def name(self):
        return f'{self.level}_{self.stat}_{self.mode}'

    @property
    def id_name(self):
        return f'{self.level}_{self.stat}_id_{self.mode}'


def get_record_modes(video_mode: RankingVideoMode | str) -> tuple[RankingMode, ...]:
    return VIDEO_MODE_TO_RECORD_MODES.get(video_mode, ())


def is_valid_ranking_level(level: str) -> bool:
    return level in LEVELS


def is_valid_ranking_mode(mode: str) -> bool:
    return mode in MODES


def get_video_num_limit(timems: int):
    if timems < 30000:
        return 10000
    elif timems < 40000:
        return 8000
    elif timems < 50000:
        return 5000
    elif timems < 60000:
        return 3000
    elif timems < 100000:
        return 1000
    return 100
