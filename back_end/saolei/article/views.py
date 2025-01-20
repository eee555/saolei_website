from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django_redis import get_redis_connection
cache = get_redis_connection("saolei_website")
from django.conf import settings
import os
from typing import List
from django.core.cache import caches


# 用文件系统管理文章
# 定时整理文章的目录文件，删除目录里没有文件的目录、添加不在目录里的文章
# 文章可以是文件夹或文件
# 任意图片png、jpg封面和md正文



# 【管理员或站长】手动事先把文章放到指定目录下后，全量更新文章目录（因为用的文件系统来管理文章）
# 文章名称存进redis，如果是文件夹（因为文章里有图片），正文必须是a.md，其他图片名字随意
# 文章名称就是文件夹名称，或文章名称.md
# 文章分类有
# 公告：网站公告、规定介绍
# 教程：扫雷教程、其他游戏教程（数织、数独等）
# 技术：开发进展、数学等
# 其他：分不了类的
# 序号必填（1-2100000000，默认999），从小到大
# 支持二级分类，二级由玩家自定义，管理员同意，例如："[60.公告]明天下雨.md"、"[3.技术.效率]破纪录像喝水.md"
# 默认其他
def update_list(request):
    if (request.user.is_staff or request.user.is_superuser) and request.method == 'GET':
    # if 1:
        if settings.DEBUG:
            article_dir = settings.BASE_DIR / "assets" / 'article'
        else:
            article_dir = os.path.join(settings.STATIC_ROOT, 'article')
        articles: List[str] = os.listdir(article_dir)
        # 先清空已有
        while cache.llen("articles") > 0:
            cache.rpop("articles")
        for article in articles:
            # 从gitee上直接clone下来的
            # if article in ["LICENSE", ".git"]:
            #     continue 
            if os.path.isdir(os.path.join(article_dir, article)):
                if os.path.isfile(os.path.join(article_dir, article, "a.md")):
                    cache.lpush("articles", article)
                else:
                    ... # 删除或往日志中记录，但问题不大
            elif article[-3:] == '.md' and article[0] == "[":
                cache.lpush("articles", article)
        return HttpResponse("..")
    else:
        return HttpResponse("别瞎玩")

# 完整文章目录
def article_list(request):
    if request.method == 'GET':
        a_list = cache.lrange("articles", 0, -1)
        # 不做过多处理（排序、分类）直接发到前端
        return JsonResponse([a.decode("utf-8") for a in a_list], safe=False)
    else:
        return HttpResponse("别瞎玩")

# http://127.0.0.1:8000/article/update_list
