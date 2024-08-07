from django.urls import path

from . import views
app_name = 'identifier'
urlpatterns = [
    path('del/', views.del_designator),
    path('add/', views.add_designator),
]