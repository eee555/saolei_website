from django.views.decorators.http import require_GET
from userprofile.decorators import staff_required
from django.http import JsonResponse, FileResponse
import os
from datetime import datetime, timezone


@require_GET
@staff_required
def get_log_file(request):
    return FileResponse(open('logs/' + request.GET.get('filename'), 'rb'), content_type='text/plain')


@require_GET
@staff_required
def get_log_dir(request):
    file_list = os.listdir('logs')
    file_stats = []
    for file in file_list:
        file_path = os.path.join('logs', file)
        file_stat = os.stat(file_path)
        file_stats.append({
            'name': file,
            'size': file_stat.st_size,
            'mtime': datetime.fromtimestamp(file_stat.st_ctime, tz=timezone.utc),
        })
    return JsonResponse(file_stats, safe=False)
