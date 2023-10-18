from django.urls import include, path

from . import views
app_name = 'msuser'
urlpatterns = [
    path('info/', views.get_info, name='info'),
    path('update/', views.update, name='update'),
    path('player_rank/', views.player_rank, name='player_rank'),
]