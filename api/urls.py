from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignupView
from .views import RunViewSet, health

router = DefaultRouter()
router.register(r'runs', RunViewSet, basename='run')

urlpatterns = [
    path('health/', health, name='health'),
    path('', include(router.urls)),
    path("signup/", SignupView.as_view(), name="signup"),

]