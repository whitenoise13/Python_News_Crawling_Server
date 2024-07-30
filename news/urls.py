from django.urls import path
from . import views

urlpatterns = [
    path('<str:category>/', views.news_by_category, name='news_by_category'),
]