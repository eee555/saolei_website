from urllib.parse import quote

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import F
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Query, Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema

from config.text_choices import MS_TextChoices
from userprofile.models import UserProfile
from .models import STNB_COEFFICIENTS, VideoModel
from .schema import VideoBaseOut
from .view_utils import video_all_fields

router = Router()
VIDEO_ACCEL_REDIRECT_PREFIX = '/internal-media/'


@router.get('/query')
@decorate_view(ratelimit(key='ip', rate='60/m'))
def video_query(request, level: MS_TextChoices.Level, mode: MS_TextChoices.Mode, o: str = 'timems', r: bool = False, ps: int = 20, page: int = 1, bmin: int = 0, bmax: int = 1000, nf: bool = False, states: list[MS_TextChoices.State] = Query(None, alias='s[]')):  # noqa: B008
    """
    - ratelimit(key='ip', rate='60/m')
    """
    if o not in video_all_fields and o != 'stnb':
        raise HttpError(400, 'Invalid sort field.')
    videos = VideoModel.objects.filter(level=level, mode=mode, bv__range=(bmin, bmax))
    if nf:
        videos = videos.filter(right_ce=0)
    if states:
        videos = videos.filter(state__in=states)
    if not request.user.is_staff:
        videos = videos.filter(ongoing_tournament=False)
    videos = videos.annotate(stnb=F('iqg') * STNB_COEFFICIENTS.get(level))
    order = ('-' if r else '') + o
    orderby = (order,) if o == 'timems' else (order, 'timems')
    videos = videos.order_by(*orderby).values(*video_all_fields, 'stnb')
    paginator = Paginator(videos, max(1, min(ps, 100)))
    return {'count': paginator.count, 'videos': list(paginator.get_page(page))}


@router.get('/query_by_id')
@decorate_view(ratelimit(key='ip', rate='60/m'))
def video_query_by_id(request, user_id: int = Query(..., alias='id')):  # noqa: B008
    """
    - ratelimit(key='ip', rate='60/m')
    """
    user = get_object_or_404(UserProfile, id=user_id)
    videos = VideoModel.objects.filter(player=user)
    if request.user != user:
        videos = videos.filter(ongoing_tournament=False)
    return list(videos.values(
        'id', 'upload_time', 'end_time', 'level', 'mode', 'timems', 'bv', 'bvs', 'state', 'video__identifier',
        'software', 'right_ce', 'flag', 'cell0', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8', 'left', 'right', 'double', 'op', 'isl', 'path', 'pluck',
    ))


def _can_request_video(request: HttpRequest, video: VideoModel):
    if not video.ongoing_tournament:
        return True
    if not request.user.is_authenticated:
        return False
    return request.user.id == video.player_id


def _video_file_response(request: HttpRequest, video_id: int):
    video = get_object_or_404(VideoModel, id=video_id)
    if not _can_request_video(request, video):
        raise HttpError(403, 'Forbidden.')
    file_name = video.file.name
    if settings.DEBUG:
        try:
            response = FileResponse(default_storage.open(file_name, 'rb'))
        except FileNotFoundError:
            raise HttpError(404, 'Video file not found.')
    else:
        response = HttpResponse()
        response['X-Accel-Redirect'] = f'{VIDEO_ACCEL_REDIRECT_PREFIX}{quote(file_name, safe="/")}'
    response['Content-Type'] = 'application/octet-stream'
    file_name_uri = quote(file_name.split('/')[-1])
    response['Content-Disposition'] = f'attachment; filename="{file_name_uri}"'
    return response


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
    ],
    custom_fields=[
        ('video__identifier', str, ''),
        ('ce', int | None, None),
    ],
)


@router.get('/preview')
@decorate_view(ratelimit(key='ip', rate='20/m'))
def video_preview(request: HttpRequest, video_id_with_extension: str = Query(..., alias='id')):  # noqa: B008
    """
    - ratelimit(key='ip', rate='20/m')
    """
    try:
        video_id = int(video_id_with_extension[:-4])
    except ValueError:
        raise HttpError(400, 'Invalid video id.')
    response = _video_file_response(request, video_id)
    response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response


@router.get('/download/{video_id}')
@decorate_view(ratelimit(key='ip', rate='20/m'))
def video_download(request: HttpRequest, video_id: int):
    """
    - ratelimit(key='ip', rate='20/m')
    """
    return _video_file_response(request, video_id)


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

    return VideoModel.objects.filter(id__gte=first, id__lt=first + count, ongoing_tournament=False)


@router.get('/detailbulk', response=list[VideoFullOut])
@decorate_view(ratelimit(key='ip', rate='1/s'))
def get_video_detail_bulk(request, first: int, count: int):
    """
    - ratelimit(key='ip', rate='1/s')

    Video id from `first` to `first + count - 1`. Hidden videos are skipped. Count is capped at 1000.
    """
    first = max(1, first)
    count = max(1, min(1000, count))

    return VideoModel.objects.filter(id__gte=first, id__lt=first + count, ongoing_tournament=False)
