from django.urls import path

from . import views
app_name = 'designator'
urlpatterns = [
    path('del/', views.del_designator),
    path('add/', views.add_designator),
]