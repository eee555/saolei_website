from django.shortcuts import render
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job, register_events
from django_apscheduler.jobstores import ConflictingIdError
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import psutil
import time, os
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from utils import ComplexEncoder


# 120点。服务器上传、下载速度、cpu占用。5秒平均、单位字节秒
def get_io_cpus(request):
    return JsonResponse({'s': cache.lrange("io_s_spds", 0, -1),
                        'r': cache.lrange("io_r_spds", 0, -1),
                        'c': cache.lrange("cpus", 0, -1)}, encoder=ComplexEncoder)

# 1个点。
# def get_io_cpu(request):
#     # print(cache.get("io_s_spd"))
#     return JsonResponse({'s': cache.get("io_s_spd"),
#                         'r': cache.get("io_r_spd")}, encoder=ComplexEncoder)

# 节流防抖的装饰器，间隔秒
def throttled(interval=5):
    class ThrottledFunction:
        def __init__(self, func):
            self.func = func
            self.interval = interval
            self.last_result = None
            self.last_call_time = None
        def __call__(self, *args, **kwargs):
            now = time.time()
            if self.last_call_time is None or now - self.last_call_time >= self.interval:
                self.last_result = self.func(*args, **kwargs)
                self.last_call_time = now
            return self.last_result
    return ThrottledFunction
    

def get_dir_size(path):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total

# 服务器总容量、录像占用大小
@throttled(interval=188)
def get_capacity(request):
    # 服务器总容量情况
    disk = psutil.disk_usage(".")
    # 录像占用容量情况
    video_size = get_dir_size(os.path.join(settings.BASE_DIR, 'assets/videos'))
    # 内存占用情况
    virtual = psutil.virtual_memory()
    return JsonResponse({"d_t": disk.total, "d_u": disk.used, "v": video_size,
                         "v_t": virtual.total, "v_u": virtual.used})



