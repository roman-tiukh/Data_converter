from django.urls import path

from .views import (ApiUsageMeView, ProfileStatsView, UsersInProjectsView, StatsTestView,
                    TopKvedsView, CompanyTypeCountView, RegisteredCompaniesCountView,
                    RegisteredFopsCountView, PepsCountView, PepRelatedPersonsCountView,
                    PepLinkedCompaniesCountView, PepRelationCategoriesCountView)
from .report_builder import ReportBuilderView

urlpatterns = [
    path('api-usage/me/', ApiUsageMeView.as_view()),
    path('profile/', ProfileStatsView.as_view()),
    path('top-kved/', TopKvedsView.as_view(), name='top_kved'),
    path('count-company-type/', CompanyTypeCountView.as_view(), name='company-type'),
    path('count-registered-companies/',
         RegisteredCompaniesCountView.as_view(),
         name='registered_companies'),
    path('count-registered-fops/',
         RegisteredFopsCountView.as_view(),
         name='registered_fops'),
    path('report-builder/',
         ReportBuilderView.as_view(),
         name='report_builder'),
    path('count-users/', UsersInProjectsView.as_view()),

    # public
    path('count-peps/', PepsCountView.as_view()),
    path('count-pep-related-persons/', PepRelatedPersonsCountView.as_view()),
    path('count-pep-related-companies/', PepLinkedCompaniesCountView.as_view()),
    path('count-pep-relation-categories/', PepRelationCategoriesCountView.as_view()),


    path('test/', StatsTestView.as_view()),
]
