from multiprocessing import get_context
from queue import Empty

from django.tasks import task

from videomanager.models import VideoModel

from .pluck_worker import calculate_pluck_worker
from .services import is_custom_pluck_video, refresh_custom_pluck_rank_for_video, update_custom_pluck_rank_for_video
from .utils import normalize_pluck

PLUCK_TIMEOUT_SECONDS = 60


def helper_custom_pluck(video: VideoModel):
    if is_custom_pluck_video(video):
        task_custom_pluck.enqueue(video.id)
    else:
        refresh_custom_pluck_rank_for_video(video)


def calculate_pluck_with_timeout(file_path: str, timeout_seconds: int = PLUCK_TIMEOUT_SECONDS):
    context = get_context('spawn')
    queue = context.Queue()
    process = context.Process(target=calculate_pluck_worker, args=(file_path, queue))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join()
        raise TimeoutError(f'Pluck calculation exceeded {timeout_seconds} seconds')

    try:
        status, payload = queue.get_nowait()
    except Empty as exc:
        raise RuntimeError(f'Pluck calculation failed with exit code {process.exitcode}') from exc

    if status == 'error':
        raise RuntimeError(payload)

    return payload


@task(priority=-1)
def task_custom_pluck(video_id: int):
    video = VideoModel.objects.get(id=video_id)
    if not is_custom_pluck_video(video):
        refresh_custom_pluck_rank_for_video(video)
        return

    pluck = normalize_pluck(calculate_pluck_with_timeout(video.file.path))
    video.pluck = pluck
    video.save(update_fields=['pluck'])
    update_custom_pluck_rank_for_video(video)
