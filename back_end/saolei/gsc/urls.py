from . import views
from django.urls import path

urlpatterns = [
    path('/info', views.get_gsc_info, name='gsc_info'),
    path('/set', views.set_gsc_field, name='set_gsc_field'),
]