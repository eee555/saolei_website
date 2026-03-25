from datetime import datetime
import logging

from django.core.files import File
from django.db import connection

from config.text_choices import MS_TextChoices
from identifier.models import Identifier
from identifier.utils import verify_identifier
from msuser.models import UserMS
from tournament.utils import video_checkin
from userprofile.models import UserProfile
from utils.exceptions import ExceptionToResponse
from utils.parser import MSVideoParser
from videomanager.models import VideoModel

logger = logging.getLogger('videomanager')


def new_video_by_file(user: UserProfile, file: File, check_tournament: bool = True, upload_time: datetime = None) -> VideoModel:
    parser = MSVideoParser(file)

    if not user.userms:
        user.userms = UserMS.objects.create()

    if not verify_identifier(parser.identifier):
        raise ExceptionToResponse(obj='identifier', category='verify')
    if not Identifier.verify(parser.identifier, user.userms) and parser.state == MS_TextChoices.State.OFFICIAL:
        parser.state = MS_TextChoices.State.IDENTIFIER

    collisions = VideoModel.objects.filter(timems=parser.timems, bv=parser.bv).filter(file_size=parser.file.size)
    for v_collision in collisions:
        if v_collision.file.read() == file.read():
            raise ExceptionToResponse(obj='file', category='collision')

    video = VideoModel.create_from_parser(parser, user)

    if check_tournament:
        video_checkin(video, parser.tournament_identifiers)

    video.save()
    video.update_redis()

    return video


def get_db_size():
    db_name = connection.settings_dict['NAME']
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SUM(data_length + index_length)
            FROM information_schema.TABLES
            WHERE table_schema = %s
        """, [db_name])
        row = cursor.fetchone()
        return int(row[0]) if row else 0
