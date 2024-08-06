from django.urls import include, path

from . import views
app_name = 'video'
urlpatterns = [
    path('upload/', views.video_upload, name='upload'),
    path('download/', views.video_download, name='download'),
    path('preview/', views.video_preview, name='preview'),
    path('get_software/', views.get_software, name='get_software'),
    path('query/', views.video_query, name='query'),
    path('query_by_id/', views.video_query_by_id, name='query_by_id'),
    path('review_queue/', views.review_queue, name='review_queue'),
    path('newest_queue/', views.newest_queue, name='newest_queue'),
    path('news_queue/', views.news_queue, name='news_queue'),
    # path('approve/', views.approve, name='approve'),
    path('freeze/', views.freeze, name='freeze'),
    path('get/',views.get_videoModel),
    path('set/',views.set_videoModel),
    # path('download/', views.video_download, name='download'),
    
]