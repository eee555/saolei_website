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
    path('saolei_import_video/', views.view_saolei_import_one_video),
    path('saolei_import_videos/', views.view_saolei_import_videos),
]
