from django.urls import path

from . import views
app_name = 'video'
urlpatterns = [
    path('get_software/', views.get_software, name='get_software'),
    path('set/', views.set_videoModel),
    path('update/', views.update_videoModel),
    path('update/batch/', views.batch_update_videoModel),
]
