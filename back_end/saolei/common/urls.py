from django.urls import path

from . import api, views

app_name = 'common'
urlpatterns = [
    path('uploadvideo/', views.video_upload, name='upload'),
    path('staff/taskdetail/', views.view_task_detail, name='task_detail'),
    path('staff/taskdelete/', views.view_delete_task, name='task_delete'),
    path('api/', api.api.urls)
]
