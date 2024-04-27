from django.urls import include, path

from . import views
app_name = 'monitor'
urlpatterns = [
    # path('io_cpu/', views.get_io_cpu, name='io_cpu'),
    path('io_cpus/', views.get_io_cpus, name='io_cpus'),
    path('capacity/', views.get_capacity, name='capacity'),
]