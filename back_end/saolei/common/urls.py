from django.urls import path

from . import views
app_name = 'common'
urlpatterns = [
    path('uploadvideo/', views.video_upload, name='upload'),
]
