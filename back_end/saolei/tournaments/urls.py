from django.urls import path

from . import views
app_name = 'tournament'
urlpatterns = [
    path('get_list/', views.get_tournament_list),
]