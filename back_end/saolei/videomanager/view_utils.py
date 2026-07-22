import struct

from config.text_choices import MS_TextChoices
from msuser.services import update_personal_record_stock as refresh_user_personal_records
from userprofile.models import UserProfile
from utils.parser import MSVideoParser
from .models import ExpandVideoModel, VideoModel

video_all_fields = [
    'id', 'upload_time', 'player__id', 'player__realname', 'timems', 'bv', 'bvs', 'state', 'level', 'mode', 'software', 'flag', 'op', 'isl', 'path', 'pluck', 'left', 'right', 'double', 'left_ce', 'right_ce',
    'double_ce', 'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8', 'left_s', 'right_s', 'double_s', 'left_ces', 'right_ces', 'double_ces', 'flag_s', 'ioe', 'thrp', 'cl_s', 'ce_s',
]
for name in [field.name for field in ExpandVideoModel._meta.get_fields()]:
    video_all_fields.append('video__' + name)


# 存量式更新用户的记录。删录像后用，恢复用户的记录。
def update_personal_record_stock(user: UserProfile):
    refresh_user_personal_records(user)


def refresh_video(video: VideoModel):
    parser = MSVideoParser(video.file)

    parser_fields = [
        'level', 'software', 'end_time', 'timems', 'bv',
        'left', 'right', 'double',
        'left_ce', 'right_ce', 'double_ce',
        'path', 'pluck', 'flag', 'op', 'isl',
        'cell0', 'cell1', 'cell2', 'cell3', 'cell4',
        'cell5', 'cell6', 'cell7', 'cell8',
    ]

    updated_fields = []

    # 1. 处理 parser 字段
    for field in parser_fields:
        new_value = getattr(parser, field)
        old_value = getattr(video, field)
        if new_value != old_value:
            setattr(video, field, new_value)
            updated_fields.append(field)

    # 2. 处理 file_size（独立来源）
    new_size = video.file.size
    if new_size != video.file_size:
        video.file_size = new_size
        updated_fields.append('file_size')

    # 3. 仅当有字段变更时才保存
    if updated_fields:
        video.save(update_fields=updated_fields)

    e_video = video.video
    e_updated_fields = []
    if e_video.identifier != parser.identifier:
        e_video.identifier = parser.identifier
        e_updated_fields.append('identifier')

    if e_updated_fields:
        e_video.save(update_fields=e_updated_fields)

    if video.state == MS_TextChoices.State.IDENTIFIER and (e_video.identifier in video.player.userms.identifiers):
        video.state = MS_TextChoices.State.OFFICIAL
        video.save(update_fields=['state'])


def generate_file_stream(queryset):
    def file_iterator():
        for video in queryset:
            if not video.file:
                continue

            filename = f'{video.player.id}_{video.player.realname}/{video.file.name.split("/")[-1]}'
            filename_bytes = filename.encode('utf-8')
            filename_len = len(filename_bytes)
            filesize = video.file.size

            # Header: 4-byte filename length + filename + 8-byte file size
            yield struct.pack('>I', filename_len)
            yield filename_bytes
            yield struct.pack('>Q', filesize)  # unsigned long long, 8 bytes

            # File content
            with video.file.open('rb') as f:
                while chunk := f.read(8192):
                    yield chunk
    return file_iterator()
