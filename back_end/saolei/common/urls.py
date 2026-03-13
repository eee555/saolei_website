from django.urls import path

from . import views
app_name = 'common'
urlpatterns = [
    path('uploadvideo/', views.video_upload, name='upload'),
    path('tasksummary/', views.view_task_summary, name='task_summary'),
    path('staff/taskdetail/', views.view_task_detail, name='task_detail'),
    path('staff/taskdelete/', views.view_delete_task, name='task_delete'),
]
