from django.urls import path

from . import views
app_name = 'msuser'
urlpatterns = [
    path('player_rank/', views.player_rank, name='player_rank'),
]
