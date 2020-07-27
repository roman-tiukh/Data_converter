from django.urls import path
from . import views

urlpatterns = [
    path('api-usage/me/', views.ApiUsageMeView.as_view())
]
