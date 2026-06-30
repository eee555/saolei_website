from datetime import datetime, timezone

from django.core.files import File
import ms_toollib as ms

from config.text_choices import MS_TextChoices
from .exceptions import ExceptionToResponse

CUSTOM_LEVELS_BY_BOARD = {
    (8, 8, 20): MS_TextChoices.Level.CUSTOM_8_8_20,
    (8, 8, 24): MS_TextChoices.Level.CUSTOM_8_8_24,
    (8, 8, 28): MS_TextChoices.Level.CUSTOM_8_8_28,
    (8, 8, 32): MS_TextChoices.Level.CUSTOM_8_8_32,
    (8, 8, 36): MS_TextChoices.Level.CUSTOM_8_8_36,
    (8, 8, 40): MS_TextChoices.Level.CUSTOM_8_8_40,
    (16, 16, 64): MS_TextChoices.Level.CUSTOM_16_16_64,
    (16, 16, 80): MS_TextChoices.Level.CUSTOM_16_16_80,
    (16, 16, 96): MS_TextChoices.Level.CUSTOM_16_16_96,
    (16, 16, 112): MS_TextChoices.Level.CUSTOM_16_16_112,
    (16, 16, 128): MS_TextChoices.Level.CUSTOM_16_16_128,
    (16, 30, 120): MS_TextChoices.Level.CUSTOM_16_30_120,
    (16, 30, 144): MS_TextChoices.Level.CUSTOM_16_30_144,
    (16, 30, 168): MS_TextChoices.Level.CUSTOM_16_30_168,
    (16, 30, 192): MS_TextChoices.Level.CUSTOM_16_30_192,
    (24, 30, 180): MS_TextChoices.Level.CUSTOM_24_30_180,
    (24, 30, 216): MS_TextChoices.Level.CUSTOM_24_30_216,
    (24, 30, 252): MS_TextChoices.Level.CUSTOM_24_30_252,
    (48, 64, 777): MS_TextChoices.Level.CUSTOM_48_64_777,
}


def create_video_from_data(file_name: str, data: bytes):
    if file_name.endswith('.avf'):
        return ms.AvfVideo(raw_data=data), MS_TextChoices.Software.AVF
    elif file_name.endswith('.evf'):
        return ms.EvfVideo(raw_data=data), MS_TextChoices.Software.EVF
    elif file_name.endswith('.rmv'):
        return ms.RmvVideo(raw_data=data), MS_TextChoices.Software.RMV
    elif file_name.endswith('.mvf'):
        return ms.MvfVideo(raw_data=data), MS_TextChoices.Software.MVF
    else:
        raise ExceptionToResponse(obj='file', category='type')


class MSVideoParser:
    file: File

    software: MS_TextChoices.Software
    level: MS_TextChoices.Level
    mode: MS_TextChoices.Mode

    state: MS_TextChoices.State
    identifier: str
    tournament_identifiers: list[str]
    end_time: datetime

    timems: int
    bv: int

    left: int
    right: int
    double: int

    left_ce: int
    right_ce: int
    double_ce: int

    path: float
    flag: int
    op: int
    isl: int

    cell0: int
    cell1: int
    cell2: int
    cell3: int
    cell4: int
    cell5: int
    cell6: int
    cell7: int
    cell8: int

    stnb: float

    def __init__(self, file: File):
        self.file = file

        v, self.software = MSVideoParser.read_file(file)

        v.parse()
        v.analyse()
        v.current_time = 1e8

        self.level = MSVideoParser.get_level_from_BaseVideo(v)

        try:
            self.state = MSVideoParser.get_state_from_review_code(v.is_valid())
        except BaseException as e:
            if e.__class__.__name__ == 'PanicException':
                raise ExceptionToResponse(obj='rust', category='panic')
            else:
                raise e
        self.identifier = v.player_identifier
        self.tournament_identifiers = v.race_identifier.split(',')
        self.end_time = datetime.fromtimestamp(v.end_time / 1000000, tz=timezone.utc)

        self.mode = str(v.mode).rjust(2, '0')
        if self.mode == '00' and v.flag == 0:
            self.mode = '12'

        self.timems = v.rtime_ms
        self.bv = v.bbbv

        self.left = v.left
        self.right = v.right
        self.double = v.double

        self.left_ce = v.lce
        self.right_ce = v.rce
        self.double_ce = v.dce

        self.path = v.path
        self.flag = v.flag
        self.op = v.op
        self.isl = v.isl

        self.cell0 = v.cell0
        self.cell1 = v.cell1
        self.cell2 = v.cell2
        self.cell3 = v.cell3
        self.cell4 = v.cell4
        self.cell5 = v.cell5
        self.cell6 = v.cell6
        self.cell7 = v.cell7
        self.cell8 = v.cell8

        self.stnb = v.stnb

    @staticmethod
    def read_file(file: File):
        data = file.read()
        file.seek(0)
        return create_video_from_data(file.name, data)

    @staticmethod
    def get_level_from_BaseVideo(v: ms.BaseVideo):
        if v.level == 3:
            return MS_TextChoices.Level.BEGINNER
        elif v.level == 4:
            return MS_TextChoices.Level.INTERMEDIATE
        elif v.level == 5:
            return MS_TextChoices.Level.EXPERT
        elif v.level == 6:
            rows = getattr(v, 'row', None)
            columns = getattr(v, 'column', None)
            mines = getattr(v, 'mine_num', None)
            if level := CUSTOM_LEVELS_BY_BOARD.get((rows, columns, mines)):
                return level
            raise ExceptionToResponse(obj='file', category='level')
        else:
            raise ExceptionToResponse(obj='file', category='level')

    @staticmethod
    def get_state_from_review_code(review_code: int):
        if review_code == 0:
            return MS_TextChoices.State.OFFICIAL
        elif review_code == 1:
            return MS_TextChoices.State.FROZEN
        elif review_code == 3:
            return MS_TextChoices.State.PLAIN
        else:
            raise ExceptionToResponse(obj='file', category='review')

    @staticmethod
    def parse_video_metadata(file: File):
        data = file.read()
        v, software = create_video_from_data(file.name, data)

        v.parse()
        v.analyse()
        v.current_time = 1e8

        level = MSVideoParser.get_level_from_BaseVideo(v)

        review_code = v.is_valid()
        state = MSVideoParser.get_state_from_review_code(review_code)
        identifier = v.player_identifier

        mode = str(v.mode).rjust(2, '0')
        if mode == '00' and v.flag == 0:
            mode = '12'

        return {
            'identifier': identifier,
            'tournament_identifier': v.race_identifier,
            'end_time': datetime.fromtimestamp(v.end_time / 1000000, tz=timezone.utc),
            'software': software,
            'level': level,
            'mode': mode,
            'state': state,
            'timems': v.rtime_ms,
            'bv': v.bbbv,
            'left': v.left,
            'right': v.right,
            'double': v.double,
            'left_ce': v.lce,
            'right_ce': v.rce,
            'double_ce': v.dce,
            'path': v.path,
            'flag': v.flag,
            'op': v.op,
            'isl': v.isl,
            'cell0': v.cell0,
            'cell1': v.cell1,
            'cell2': v.cell2,
            'cell3': v.cell3,
            'cell4': v.cell4,
            'cell5': v.cell5,
            'cell6': v.cell6,
            'cell7': v.cell7,
            'cell8': v.cell8,
        }
