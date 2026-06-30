import traceback

from utils.parser import create_video_from_data


def calculate_pluck_worker(file_path: str, queue):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

        parsed_video, _ = create_video_from_data(file_path, data)
        parsed_video.parse()
        parsed_video.analyse()
        parsed_video.analyse_for_features(['pluck'])
        parsed_video.current_time = 1e8
        queue.put(('success', parsed_video.pluck))
    except BaseException:
        queue.put(('error', traceback.format_exc()))
