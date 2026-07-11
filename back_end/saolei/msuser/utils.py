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


@dataclass(frozen=True, init=False)
class RankingField:
    level: RankingLevel
    stat: RankingStat
    mode: RankingMode

    def __init__(self, level_or_name: RankingLevel | str, stat: RankingStat | None = None, mode: RankingMode | None = None):
        if stat is None and mode is None:
            level, parsed_stat, parsed_mode = self.parse_name(level_or_name)
        elif stat is not None and mode is not None:
            level = level_or_name
            parsed_stat = stat
            parsed_mode = mode
        else:
            raise TypeError('RankingField expects either a name string or level, stat, mode')

        object.__setattr__(self, 'level', level)
        object.__setattr__(self, 'stat', parsed_stat)
        object.__setattr__(self, 'mode', parsed_mode)

    @staticmethod
    def parse_name(name: str) -> tuple[RankingLevel, RankingStat, RankingMode]:
        parts = name.split('_')
        if len(parts) == 3:
            level, stat, mode = parts
        elif len(parts) == 4 and parts[2] == 'id':
            level, stat, _, mode = parts
        else:
            raise ValueError(f'Invalid ranking field name: {name}')
        return level, stat, mode

    @property
    def name(self):
        return f'{self.level}_{self.stat}_{self.mode}'

    @property
    def id_name(self):
        return f'{self.level}_{self.stat}_id_{self.mode}'

    @property
    def update_names(self):
        return [self.name, self.id_name]


@dataclass(frozen=True)
class RankingValue:
    value: int | float
    video_id: int | None


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
