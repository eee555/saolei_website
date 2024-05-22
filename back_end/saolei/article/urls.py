from django.urls import include, path

from . import views
app_name = 'article'
urlpatterns = [
    path('update_list/', views.update_list, name='update_list'),
    path('articles/', views.article_list, name='article_list'),
]


