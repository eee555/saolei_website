from django.urls import include, path

from . import views
app_name = 'msuser'
urlpatterns = [
    path('info_abstract/', views.get_info_abstract, name='info_abstract'),
    path('info/', views.get_info, name='info'),
    path('records/', views.get_records, name='records'),
    path('update_realname/', views.update_realname, name='update_realname'),
    path('update_avatar/', views.update_avatar, name='update_avatar'),
    path('update_signature/', views.update_signature, name='update_signature'),
    path('player_rank/', views.player_rank, name='player_rank'),
    path('identifiers/', views.get_identifiers, name='identifiers'),
]