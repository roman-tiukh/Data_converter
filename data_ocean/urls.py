from django.urls import path, include
from django.contrib import admin

from data_ocean.views.company_views import BylawView, CompanyTypeView, CompanyView, AssigneeView, BancruptcyReadjustmentView, CompanyDetailView, CompanyToKvedView, ExchangeDataCompanyView, FounderFullView, PredecessorView, CompanyToPredecessorView, SignerView, TerminationStartedView
from data_ocean.views.kved_views import KvedView
from data_ocean.views.ratu_views import CitydistrictView, CityView, DistrictView, RegionView, StreetView
from data_ocean.views.rfop_views import RfopView, FopView
from data_ocean.views.ruo_views import RuoView

app_name = 'data_ocean.apps.DataOceanConfig'

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('rfop/', RfopView.as_view({'get':'list'})),
    path('rfop/<int:pk>', RfopView.as_view({'get':'retrieve'})),
    path('fop/', FopView.as_view({'get':'list'})),
    path('fop/<int:pk>', FopView.as_view({'get':'retrieve'})),
    path('ruo/', RuoView.as_view({'get':'list'})),
    path('ruo/<int:pk>', RuoView.as_view({'get':'retrieve'})),
    path('kved/', KvedView.as_view({'get':'list'})),
    path('kved/<int:pk>', KvedView.as_view({'get':'retrieve'})),
    path('region/', RegionView.as_view({'get':'list'})),
    path('region/<int:pk>', RegionView.as_view({'get':'retrieve'})),
    path('city/', CityView.as_view({'get':'list'})),
    path('city/<int:pk>', CityView.as_view({'get':'retrieve'})),
    path('street/', StreetView.as_view({'get':'list'})),
    path('street/<int:pk>', StreetView.as_view({'get':'retrieve'})),
    path('citydistrict/', CitydistrictView.as_view({'get':'list'})),
    path('citydistrict/<int:pk>', CitydistrictView.as_view({'get':'retrieve'})),
    path('district/', DistrictView.as_view({'get':'list'})),
    path('district/<int:pk>', DistrictView.as_view({'get':'retrieve'})),
    path('bylaw/', BylawView.as_view({'get':'list'})),
    path('bylaw/<int:pk>', BylawView.as_view({'get':'retrieve'})),
    path('company_type/', CompanyTypeView.as_view({'get':'list'})),
    path('company_type/<int:pk>', CompanyTypeView.as_view({'get':'retrieve'})),
    path('company/', CompanyView.as_view({'get':'list'})),
    path('company/<int:pk>', CompanyView.as_view({'get':'retrieve'})),
    path('assignee/', AssigneeView.as_view({'get':'list'})),
    path('assignee/<int:pk>', AssigneeView.as_view({'get':'retrieve'})),
    path('bancruptcy_readjustment/', BancruptcyReadjustmentView.as_view({'get':'list'})),
    path('bancruptcy_readjustment/<int:pk>', BancruptcyReadjustmentView.as_view({'get':'retrieve'})),
    path('company_detail/', CompanyDetailView.as_view({'get':'list'})),
    path('company_detail/<int:pk>', CompanyDetailView.as_view({'get':'retrieve'})),
    path('company_to_kved/', CompanyToKvedView.as_view({'get':'list'})),
    path('company_to_kved/<int:pk>', CompanyToKvedView.as_view({'get':'retrieve'})),
    path('exchange_data_company/', ExchangeDataCompanyView.as_view({'get':'list'})),
    path('exchange_data_company/<int:pk>', ExchangeDataCompanyView.as_view({'get':'retrieve'})),
    path('founder_full/', FounderFullView.as_view({'get':'list'})),
    path('founder_full/<int:pk>', FounderFullView.as_view({'get':'retrieve'})),
    path('predecessor/', PredecessorView.as_view({'get':'list'})),
    path('predecessor/<int:pk>', PredecessorView.as_view({'get':'retrieve'})),
    path('company_to_predecessor/', CompanyToPredecessorView.as_view({'get':'list'})),
    path('company_to_predecessor/<int:pk>', CompanyToPredecessorView.as_view({'get':'retrieve'})),
    path('signer/', SignerView.as_view({'get':'list'})),
    path('signer/<int:pk>', SignerView.as_view({'get':'retrieve'})),
    path('termination_started/', TerminationStartedView.as_view({'get':'list'})),
    path('termination_started/<int:pk>', TerminationStartedView.as_view({'get':'retrieve'})),
]