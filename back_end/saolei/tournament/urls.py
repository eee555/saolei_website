from django.urls import path

from . import views
app_name = 'tournament'
urlpatterns = [
    path('get_list/', views.get_tournament_list),
    path('set/', views.set_tournament),
    path('get/', views.get_tournament),
    path('participants/', views.get_participant_list),
    path('validate/', views.validate_tournament),
    path('download/', views.download_all_videos),
    path('download/participant/', views.download_videos_participant),
    path('get_news/', views.get_tournament_news),
    path('get_videos/participant/', views.get_participant_videos),
]
