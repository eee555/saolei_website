from django.urls import include, path

from . import views
app_name = 'video'
urlpatterns = [
    path('upload/', views.video_upload, name='upload'),
    path('download/', views.video_download, name='download'),
    path('preview/', views.video_preview, name='preview'),
    path('get_software/', views.get_software, name='get_software'),
    path('query/', views.video_query, name='query'),
    # path('download/', views.video_download, name='download'),
    
]