from django.urls import path, include
from django.contrib import admin

from data_ocean.views.kved_views import KvedView
from data_ocean.views.ratu_views import CitydistrictView, CityView, DistrictView, RegionView, StreetView
from data_ocean.views.rfop_views import RfopView, FopView
from data_ocean.views.ruo_views import RuoView

app_name = 'data_ocean.apps.DataOceanConfig'

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('rfop/', RfopView.as_view()),
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
]