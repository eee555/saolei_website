from django_ratelimit.decorators import ratelimit
from ninja import Router
from ninja.decorators import decorate_view
from ninja.orm import create_schema

from config.text_choices import MS_TextChoices
from .models import VideoModel

router = Router()


VideoBaseOut = create_schema(
    VideoModel,
    fields=[
        'id', 'player',
        'software', 'level', 'mode', 'state',
        'cl', 'ce', 'timems', 'bv',
        'upload_time', 'end_time',
    ],
)


VideoFullOut = create_schema(
    VideoModel,
    fields=[
        'id', 'player',
        'software', 'level', 'mode', 'state',
        'timems', 'bv', 'path', 'flag', 'op', 'isl',
        'upload_time', 'end_time', 'file_size',
        'left', 'right', 'double', 'cl',
        'left_ce', 'right_ce', 'double_ce', 'ce',
        'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8',
        'video__identifier',
    ],
)


@router.get('/review_queue', response=list[VideoBaseOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def get_review_queue(request):
    """
    - ratelimit(key='ip', rate='1/s')
    """
    videos = VideoModel.objects.filter(state=MS_TextChoices.State.PLAIN)
    if not request.user.is_staff:
        videos = videos.filter(ongoing_tournament=False)

    return videos


@router.get('/infobulk', response=list[VideoBaseOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def get_video_info_bulk(request, first: int, count: int):
    """
    - ratelimit(key='ip', rate='1/s')

    Video id from `first` to `first + count - 1`. Hidden videos are skipped. Count is capped at 5000.
    """
    first = max(1, first)
    count = max(1, min(5000, count))

    return VideoModel.objects.filter(id_gte=first, id_lt=first + count, ongoing_tournament=False)


@router.get('/detailbulk', response=list[VideoFullOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def get_video_detail_bulk(request, first: int, count: int):
    """
    - ratelimit(key='ip', rate='1/s')

    Video id from `first` to `first + count - 1`. Hidden videos are skipped. Count is capped at 1000.
    """
    first = max(1, first)
    count = max(1, min(1000, count))

    return VideoModel.objects.filter(id_gte=first, id_lt=first + count, ongoing_tournament=False)
