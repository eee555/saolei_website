from django.urls import path

from . import views
app_name = 'accountlink'
urlpatterns = [
    path('add/', views.add_link),
    path('delete/', views.delete_link),
    path('get/', views.get_link),
    path('update/', views.update_link),
    path('verify/', views.verify_link),
    path('unverify/', views.unverify_link),
]
