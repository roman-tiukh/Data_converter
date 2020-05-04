from django.urls import path
from data_ocean.views.rfop_views import RfopView
from data_ocean.views.ruo_views import RuoView
from data_ocean.views.ratu_views import RegionView, DistrictView, CityView, CitydistrictView, StreetView
from data_ocean.views.kved_views import KvedView

app_name = 'data_ocean.apps.DataOceanConfig'

urlpatterns = [
    path('rfop/', RfopView.as_view()),
    path('ruo/', RuoView.as_view()),
    path('kved/', KvedView.as_view({'get':'list'})),
    path('kved/<int:pk>', KvedView.as_view({'get':'retrieve'})),
    path('region/', RegionView.as_view()),
    path('city/', CityView.as_view()),
    path('street/', StreetView.as_view()),
    path('citydistrict/', CitydistrictView.as_view()),
    path('district/', DistrictView.as_view()),
]