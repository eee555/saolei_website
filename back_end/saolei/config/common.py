from datetime import timedelta


TASK_CLEANUP_CONFIGS = [
    {
        'task_path': 'videomanager.tasks.task_video_pluck',
        'expires': timedelta(days=1),
    },
    {
        'task_path': 'accountlink.tasks.task_saolei_video_import',
        'expires': timedelta(days=7),
    },
    {
        'task_path': 'accountlink.tasks.task_saolei_video_import_bulk',
        'expires': timedelta(days=7),
    },
]
