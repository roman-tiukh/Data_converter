from django.urls import path

from . import views
from .views import TopKvedsView, RegisteredCompaniesCountView

urlpatterns = [
    path('api-usage/me/', views.ApiUsageMeView.as_view()),
    path('top-kved/', TopKvedsView.as_view(), name='top_kved'),
    path('registered-companies/',
         RegisteredCompaniesCountView.as_view(), name='registered_companies'),
]
