from django.urls import path

from . import views
app_name = 'video'
urlpatterns = [
    path('get_software/', views.get_software, name='get_software'),
    path('newest_queue/', views.newest_queue, name='newest_queue'),
    path('newest_queue/remove/', views.remove_from_newest_queue),
    # path('approve/', views.approve, name='approve'),
    # path('freeze/', views.freeze, name='freeze'),
    path('get/', views.get_videoModel),
    path('set/', views.set_videoModel),
    path('update/', views.update_videoModel),
    path('update/batch/', views.batch_update_videoModel),
]
