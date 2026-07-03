import math

from timeout_decorator import timeout

from config.customranking import CUSTOM_PLUCK_LEVELS, CUSTOM_PLUCK_MODES
from utils.parser import create_video_from_data
from .config import PLUCK_TIMEOUT_SECONDS


def is_custom_pluck_video(video) -> bool:
    return (
        video.level in CUSTOM_PLUCK_LEVELS
        and video.mode in CUSTOM_PLUCK_MODES
    )


def normalize_pluck(value) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        return None
    return value


@timeout(PLUCK_TIMEOUT_SECONDS, use_signals=False, timeout_exception=TimeoutError)
def calculate_pluck(file_path: str):
    with open(file_path, 'rb') as file:
        data = file.read()

    parsed_video, _ = create_video_from_data(file_path, data)
    parsed_video.parse()
    parsed_video.analyse()
    parsed_video.analyse_for_features(['pluck'])
    parsed_video.current_time = 1e8
    return parsed_video.pluck
