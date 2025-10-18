from django.urls import path

from . import views
from .views import gsc
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
    path('get_gsc_tournament/', gsc.get_GSC_tournament),
    path('new_gsc/', gsc.new_GSC_tournament),
    path('gscregister/', gsc.register_GSCParticipant),
    path('gscinfo/', gsc.get_gscinfo),
    path('gsc/award/', gsc.award_GSC),
    path('gsc/participants/', gsc.get_participant_list),
    path('gsc/refresh/', gsc.refresh_GSCParticipant),
]
