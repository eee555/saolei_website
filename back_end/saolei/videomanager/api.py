from urllib.parse import quote

from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from ninja import Query, Router
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.orm import create_schema

from config.text_choices import MS_TextChoices
from .models import VideoModel
from .schema import VideoBaseOut

router = Router()
VIDEO_ACCEL_REDIRECT_PREFIX = '/internal-media/'


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
