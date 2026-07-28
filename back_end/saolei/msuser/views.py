import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django_redis import get_redis_connection

from utils import ComplexEncoder

logger = logging.getLogger('userprofile')
cache = get_redis_connection('saolei_website')


# 从redis获取用户排行榜
@require_GET
def player_rank(request):
    data = request.GET
    num_player = cache.zcard(data['ids'])
    start_idx = 20 * (int(data['page']) - 1)
    if start_idx >= num_player:
        start_idx = num_player // 20 * 20
    if num_player % 20 == 0 and num_player > 0:
        start_idx -= 20
    desc_flag = True if data['reverse'] == 'true' else False
    res = cache.sort(data['ids'], by=data['sort_by'], get=json.loads(data['indexes']), desc=desc_flag, start=start_idx, num=20)
    response = {
        'total_page': num_player // 20 + 1,
        'players': res,
    }
    return JsonResponse(response, safe=False, encoder=ComplexEncoder)
