from django.urls import path
from .views import RfopView
from .views import RuoView

from . import views
from .views import RegionView,DistrictView,CityView,CitydistrictView,StreetView
app_name = 'ratu.apps.RatuConfig'
urlpatterns = [
    path('', views.index, name='index'),
    path('rfop/', RfopView.as_view()),
    path('ruo/', RuoView.as_view()),
    path('region/', RegionView.as_view()),
    path('city/', CityView.as_view()),
    path('street/', StreetView.as_view()),
    path('citydistrict/', CitydistrictView.as_view()),
    path('district/', DistrictView.as_view()),
]

