# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import VideoModel


@admin.register(VideoModel)
class VideoAdmin(admin.ModelAdmin):
    # 指定后台网页要显示的字段
    list_display = ("id", "mode", "state", "level", "player", "file", "upload_time", "state", "level", "timems", "bv")
