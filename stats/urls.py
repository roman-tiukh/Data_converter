from django.urls import path

from . import views
from .views import TopKvedsView

urlpatterns = [
    path('api-usage/me/', views.ApiUsageMeView.as_view()),
    path('top-kved/', TopKvedsView.as_view(), name='top_kved'),
]
