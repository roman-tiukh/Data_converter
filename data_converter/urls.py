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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_auth.views import PasswordResetConfirmView
from rest_framework import routers

from business_register.views.company_views import (CompanyViewSet, CompanyUkrViewSet, CompanyUkViewSet,
                                                   HistoricalAssigneeView,
                                                   HistoricalBancruptcyReadjustmentView, HistoricalCompanyView,
                                                   HistoricalCompanyDetailView, HistoricalCompanyToKvedView,
                                                   HistoricalCompanyToPredecessorView,
                                                   HistoricalExchangeDataCompanyView, HistoricalFounderView,
                                                   HistoricalSignerView, HistoricalTerminationStartedView)
from business_register.views.fop_views import FopViewSet
from business_register.views.kved_views import KvedViewSet
from business_register.views.pep_views import PepViewSet
from business_register.views.sanction_views import (CountrySanctionViewSet,
                                                    PersonSanctionViewSet,
                                                    CompanySanctionViewSet)
from data_ocean.views import RegisterView, SchemaView
from location_register.views.drv_views import DrvBuildingViewSet
from location_register.views.ratu_views import (RatuRegionView, RatuCityView, RatuStreetView,
                                                RatuCityDistrictView, RatuDistrictView)
from location_register.views.koatuu_views import (KoatuuFirstLevelViewSet,
                                                  KoatuuSecondLevelViewSet,
                                                  KoatuuThirdLevelViewSet,
                                                  KoatuuFourthLevelViewSet)
from users.views import CustomRegistrationView, CustomRegistrationConfirmView, LandingMailView, RefreshTokenView

router = routers.DefaultRouter()

router.register(r'fop', FopViewSet, basename='fop')
router.register(r'kved', KvedViewSet, basename='kved')
router.register(r'region', RatuRegionView, basename='region')
router.register(r'city', RatuCityView, basename='city')
router.register(r'street', RatuStreetView, basename='street')
router.register(r'citydistrict', RatuCityDistrictView, basename='citydistrict')
router.register(r'district', RatuDistrictView, basename='district')
router.register(r'drvbuilding', DrvBuildingViewSet, basename='drvbuilding')
router.register(r'company/ukr', CompanyUkrViewSet, basename='company_ukr')
router.register(r'company/uk', CompanyUkViewSet, basename='company_uk')
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'koatuu-first-level', KoatuuFirstLevelViewSet, basename='koatuu_first_level')
router.register(r'koatuu-second-level', KoatuuSecondLevelViewSet, basename='koatuu_second_level')
router.register(r'koatuu-third-level', KoatuuThirdLevelViewSet, basename='koatuu_third_level')
router.register(r'koatuu-fourth-level', KoatuuFourthLevelViewSet, basename='koatuu_fourth_level')
router.register(r'register', RegisterView, basename='register')
router.register(r'historical-assignee', HistoricalAssigneeView, basename='historical_assignee')
router.register(r'historical-bancruptcy-readjustment', HistoricalBancruptcyReadjustmentView,
                basename='historical_bancruptcy_readjustment')
router.register(r'historical-company', HistoricalCompanyView, basename='historical_company')
router.register(r'historical-company-detail', HistoricalCompanyDetailView, basename='historical_company_detail')
router.register(r'historical-company-to-kved', HistoricalCompanyToKvedView, basename='historical_company_to_kved')
router.register(r'historical-company-to-predecessor', HistoricalCompanyToPredecessorView,
                basename='historical_company_to_predecessor')
router.register(r'historical-exchange-data-company', HistoricalExchangeDataCompanyView,
                basename='historical_exchange_data_company')
router.register(r'historical-founder', HistoricalFounderView, basename='historical_founder')
router.register(r'historical-signer', HistoricalSignerView, basename='historical_signer')
router.register(r'historical-termination-started', HistoricalTerminationStartedView,
                basename='historical_termination_started')
router.register(r'pep', PepViewSet, basename='pep')
router.register('sanction/country', CountrySanctionViewSet, basename='sanction_country')
router.register('sanction/person', PersonSanctionViewSet, basename='sanction_person')
router.register('sanction/company', CompanySanctionViewSet, basename='sanction_company')

urlpatterns = [
    path('api/stats/', include('stats.urls')),

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

    path('api/rest-auth/registration/', CustomRegistrationView.as_view(), name='custom_registration'),
    path(
        'api/rest-auth/registration-confirm/<int:user_id>/<str:confirm_code>/',
        CustomRegistrationConfirmView.as_view(),
        name='custom_registration_confirm',
    ),
    path('api/rest-auth/refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),

    # path('api/rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/rest-auth/', include('rest_auth.urls')),

    path('api/users/', include('users.urls')),

    path('api/payment/', include(('payment_system.urls', 'payment_system'), namespace='payment_system')),

    path('api/landing_mail/', LandingMailView.as_view(), name='landing_mail'),

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

    path('api/', include((router.urls, 'registers'), namespace='registers')),
]

if settings.DEBUG:
    urlpatterns += [
        path('debug-rest-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
