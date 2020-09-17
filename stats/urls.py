from django.urls import path

from . import views
from .views import (TopKvedsView, CompanyTypeCountView, RegisteredCompaniesCountView,
                    RegisteredFopsCountView)
from .report_builder import ReportBuilderView

urlpatterns = [
    path('api-usage/me/', views.ApiUsageMeView.as_view()),
    path('profile/', views.ProfileStatsView.as_view()),
    path('top-kved/', TopKvedsView.as_view(), name='top_kved'),
    path('company-type/', CompanyTypeCountView.as_view(), name='company-type'),
    path('registered-companies/',
         RegisteredCompaniesCountView.as_view(), name='registered_companies'),
    path('registered-fops/',
         RegisteredFopsCountView.as_view(), name='registered_fops'),
    path('report-builder/',
         ReportBuilderView.as_view(), name='report_builder'),
]
