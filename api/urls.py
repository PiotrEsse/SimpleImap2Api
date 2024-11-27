from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'imap-servers', views.IMAPServerViewSet, basename='imap-server')
router.register(r'emails', views.EmailViewSet, basename='email')

urlpatterns = [
    path('', include(router.urls)),
]
