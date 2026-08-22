from ninja.orm import create_schema

from .models import VideoModel

VideoBaseOut = create_schema(
    VideoModel,
    fields=[
        'id', 'player',
        'software', 'level', 'mode', 'state',
        'cl', 'ce', 'timems', 'bv',
        'upload_time', 'end_time',
    ],
)
