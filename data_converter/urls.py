"""data_converter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.urls import include, path, re_path
from rest_auth.views import PasswordResetConfirmView
from rest_framework import routers

from data_ocean.views import RegisterView, SchemaView
from business_register.views.company_views import CompanyView, HistoricalCompanyView
from business_register.views.kved_views import KvedView
from business_register.views.fop_views import FopView
from location_register.views.ratu_viewsets import RatuRegionView, RatuCityView, RatuStreetView, RatuCityDistrictView, RatuDistrictView
from location_register.views.drv_viewsets import DrvBuildingViewSet
from users.views import CustomRegisterView, CustomRegisterConfirmView

router = routers.DefaultRouter()

router.register(r'fop', FopView, basename='fop')
router.register(r'kved', KvedView, basename='kved')
router.register(r'region', RatuRegionView, basename='region')
router.register(r'city', RatuCityView, basename='city')
router.register(r'street', RatuStreetView, basename='street')
router.register(r'citydistrict', RatuCityDistrictView, basename='citydistrict')
router.register(r'district', RatuDistrictView, basename='district')
router.register(r'drvbuilding', DrvBuildingViewSet, basename='drvbuilding')
router.register(r'company', CompanyView, basename='company')
router.register(r'register', RegisterView, basename='register')
router.register(r'historical-company', HistoricalCompanyView, basename='historical_company')

urlpatterns = [

    path('admin/', admin.site.urls),

    re_path(
        r'^api/rest-auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)'
        r'/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    path('', TemplateView.as_view(template_name='users/index.html')),
    path('api/accounts/profile/', TemplateView.as_view(template_name='users/profile.html')),
    path('api/accounts/', include('allauth.urls')),

    path('api/rest-auth/registration/', CustomRegisterView.as_view(), name='custom_registration'),
    path(
        'api/rest-auth/registration-confirm/<int:user_id>/<str:confirm_code>/',
        CustomRegisterConfirmView.as_view(),
        name='custom_registration_confirm',
    ),

    # path('api/rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/rest-auth/', include('rest_auth.urls')),

    path('api/users/', include('users.urls')),

    path('api/', include(router.urls)),

    re_path(
        r'^schema/swagger(?P<format>\.json|\.yaml)$',
        SchemaView.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    re_path(
        r'^schema/swagger/$',
        SchemaView.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^schema/redoc/$',
        SchemaView.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path('debug-rest-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]
