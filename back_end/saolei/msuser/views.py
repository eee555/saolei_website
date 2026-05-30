import decimal
import json
import logging

from django.http import HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET
from django_ratelimit.decorators import ratelimit
from django_redis import get_redis_connection

from config.global_settings import GameModes, RankingGameStats
from userprofile.models import UserProfile
from utils import ComplexEncoder

logger = logging.getLogger('userprofile')
cache = get_redis_connection('saolei_website')

# 根据id获取用户的基本资料、扫雷记录
# 无需登录就可获取


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


# 获取我的地盘里的姓名、全部纪录
@ratelimit(key='ip', rate='15/m')
@require_GET
def get_records(request):
    if not (user_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    ms_user = user.userms

    response = {'id': user_id}
    for mode in GameModes:
        value = {}
        for stat in RankingGameStats:
            value[stat] = ms_user.getrecords_level(stat, mode)
            value[f'{stat}_id'] = ms_user.getrecordIDs_level(stat, mode)
        response[f'{mode}_record'] = json.dumps(value, cls=DecimalEncoder)
    return JsonResponse(response)


# 鼠标移到人名上时，展现头像、姓名、id、记录
@ratelimit(key='ip', rate='5/s')
@require_GET
def get_info_abstract(request):
    # 此处要防攻击
    if not (user_id := request.GET.get('id')):
        return HttpResponseBadRequest()
    if not (user := UserProfile.objects.filter(id=user_id).first()):
        return HttpResponseNotFound()
    ms_user = user.userms

    response = {
        'record_abstract': json.dumps(
            {
                'timems': ms_user.getrecords_level('timems', 'std'),
                'bvs': ms_user.getrecords_level('bvs', 'std'),
                'timems_id': ms_user.getrecordIDs_level('timems', 'std'),
                'bvs_id': ms_user.getrecordIDs_level('bvs', 'std'),
            },
            cls=DecimalEncoder,
        ),
    }

    return JsonResponse(response)


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
