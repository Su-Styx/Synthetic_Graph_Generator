from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuickViewUploadView, SignupView
from .views import RunViewSet, health
from .views import WorkloadQueryView
from .views import FileUploadView

router = DefaultRouter()
router.register(r'runs', RunViewSet, basename='run')

urlpatterns = [
    path('health/', health, name='health'),
    path('', include(router.urls)),
    path("signup/", SignupView.as_view(), name="signup"),
    path("workload-query/", WorkloadQueryView.as_view(), name="workload-query"),
    path("quick-view/", QuickViewUploadView.as_view(), name="quick-view-upload"),
    path("upload/", FileUploadView.as_view(), name="file-upload"),

    ]
