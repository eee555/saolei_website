from django.urls import path

from . import views
app_name = 'identifier'
urlpatterns = [
    path('del/', views.del_identifier),
    path('add/', views.add_identifier),
    path('refresh/', views.refresh_identifier),
    path('add/staff/', views.staff_add_identifier),
    path('del/staff/', views.staff_del_identifier),
    path('get/staff/', views.staff_get_identifier),
    path('approve/staff/', views.staff_approve_identifier),
]
