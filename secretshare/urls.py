from django.urls import path

from . import views

app_name = "secretshare"

urlpatterns = [
    path("<uuid:pk>/", views.secret_detail, name="secret-detail"),
]
