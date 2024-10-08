"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from pm.views import DomainViewSet, ProjectViewSet, TaskViewSet, SubtaskViewSet
from pm.views import CommentViewSet, AttachmentViewSet, ActivityViewSet
from notifications.views import NotificationViewSet

admin.site.site_header = "PM Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "PM"

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"domains", DomainViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"subtasks", SubtaskViewSet)
router.register(r"comments", CommentViewSet)
router.register(r"attachments", AttachmentViewSet)
router.register(r"activities", ActivityViewSet)
router.register(r"notifications", NotificationViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    # Simple JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # REST framework's login and logout views
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    # Serve user-uploaded media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
