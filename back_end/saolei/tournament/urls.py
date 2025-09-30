from django.urls import path

from . import views
app_name = 'tournament'
urlpatterns = [
    path('get_list/', views.get_tournament_list),
    path('get_gsc_tournament/', views.get_GSC_tournament),
    path('new_gsc/', views.new_GSC_tournament),
    path('set/', views.set_tournament),
    path('get/', views.get_tournament),
    path('validate/', views.validate_tournament),
]
