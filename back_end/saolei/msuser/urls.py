from django.urls import include, path

from . import views
app_name = 'msuser'
urlpatterns = [
    path('info_abstract/', views.get_info_abstract, name='info_abstract'),
    path('info/', views.get_info, name='info'),
    path('records/', views.get_records, name='records'),
    path('update/', views.update, name='update'),
    path('player_rank/', views.player_rank, name='player_rank'),
]