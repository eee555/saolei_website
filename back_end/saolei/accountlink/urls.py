from django.urls import path

from . import views
app_name = 'accountlink'
urlpatterns = [
    path('add/', views.add_link),
    path('get/', views.get_link),
]