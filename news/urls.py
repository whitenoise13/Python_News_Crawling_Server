from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('<str:category>/', news_by_category, name='news_by_category'),  # 웹 스크래핑 엔드포인트
]
