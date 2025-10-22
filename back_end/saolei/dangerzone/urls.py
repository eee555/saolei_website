from django.urls import path

from . import views

urlpatterns = [
    path('delete_user/', views.delete_user),
    path('flush_database/', views.flush_database),
    path('register/', views.quick_register),
]
