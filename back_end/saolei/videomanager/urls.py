from django.urls import path

from . import views
app_name = 'video'
urlpatterns = [
    path('set/', views.set_videoModel),
    path('update/', views.update_videoModel),
    path('update/batch/', views.batch_update_videoModel),
]
