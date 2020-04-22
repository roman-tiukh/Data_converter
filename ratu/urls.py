from django.urls import path
from ratu.views.rfop_views import RfopView
from ratu.views.ruo_views import RuoView
from ratu.views.ratu_views import RegionView, DistrictView, CityView, CitydistrictView, StreetView

app_name = 'ratu.apps.RatuConfig'

urlpatterns = [
    path('rfop/', RfopView.as_view()),
    path('ruo/', RuoView.as_view()),
    path('region/', RegionView.as_view()),
    path('city/', CityView.as_view()),
    path('street/', StreetView.as_view()),
    path('citydistrict/', CitydistrictView.as_view()),
    path('district/', DistrictView.as_view()),
]