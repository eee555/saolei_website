from django.urls import path

from . import views
app_name = 'msuser'
urlpatterns = [
    path('info_abstract/', views.get_info_abstract, name='info_abstract'),
    path('records/', views.get_records, name='records'),
    path('player_rank/', views.player_rank, name='player_rank'),
]
