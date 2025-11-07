from django.core.files import File
from config.text_choices import MS_TextChoices
from .exceptions import ExceptionToResponse
import ms_toollib as ms
from datetime import timezone, datetime


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

        v.parse_video()
        v.analyse()
        v.current_time = 1e8

        self.level = MSVideoParser.get_level_from_BaseVideo(v)

        self.state = MSVideoParser.get_state_from_review_code(v.is_valid())
        self.identifier = v.player_identifier
        self.tournament_identifiers = v.race_identifier.split(',')
        self.end_time = datetime.fromtimestamp(v.end_time / 1000000, tz=timezone.utc)
        print(self.end_time)

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
        if file.name.endswith('.avf'):
            v = ms.AvfVideo(raw_data=data)
            software = MS_TextChoices.Software.AVF
        elif file.name.endswith('.evf'):
            v = ms.EvfVideo(raw_data=data)
            software = MS_TextChoices.Software.EVF
        elif file.name.endswith('.rmv'):
            v = ms.RmvVideo(raw_data=data)
            software = MS_TextChoices.Software.RMV
        elif file.name.endswith('.mvf'):
            v = ms.MvfVideo(raw_data=data)
            software = MS_TextChoices.Software.MVF
        else:
            raise ExceptionToResponse(obj='file', category='type')

        return v, software

    @staticmethod
    def get_level_from_BaseVideo(v: ms.BaseVideo):
        if v.level == 3:
            return MS_TextChoices.Level.BEGINNER
        elif v.level == 4:
            return MS_TextChoices.Level.INTERMEDIATE
        elif v.level == 5:
            return MS_TextChoices.Level.EXPERT
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
        if file.name.endswith('.avf'):
            v = ms.AvfVideo(raw_data=data)
            software = MS_TextChoices.Software.AVF
        elif file.name.endswith('.evf'):
            v = ms.EvfVideo(raw_data=data)
            software = MS_TextChoices.Software.EVF
        elif file.name.endswith('.rmv'):
            v = ms.RmvVideo(raw_data=data)
            software = MS_TextChoices.Software.RMV
        elif file.name.endswith('.mvf'):
            v = ms.MvfVideo(raw_data=data)
            software = MS_TextChoices.Software.MVF
        else:
            raise ExceptionToResponse(obj='file', category='type')

        v.parse_video()
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