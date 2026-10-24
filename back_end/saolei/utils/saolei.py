from datetime import datetime


class SaoleiVideoInfo:
    id: int
    level: str
    bv: int
    timems: int
    nf: bool
    upload_time: datetime
    state: str

    def __init__(self, video_id: int, level: int, bv: int, timems: int, nf: bool, upload_time: datetime, verified: bool):
        self.id = video_id
        self.level = level
        self.bv = bv
        self.timems = timems
        self.nf = nf
        self.upload_time = upload_time
        self.verified = verified

    def dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'bv': self.bv,
            'timems': self.timems,
            'nf': self.nf,
            'upload_time': self.upload_time,
            'verified': self.verified,
        }

    @property
    def url(self):
        return f'http://saolei.wang/Video/Show.asp?Id={self.id}'
