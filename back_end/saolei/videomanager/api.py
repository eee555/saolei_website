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
        'upload_time', 'ongoing_tournament',
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
