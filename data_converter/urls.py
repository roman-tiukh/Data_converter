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
from django.conf.urls import url
from django.views.generic import TemplateView
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_auth.views import PasswordResetConfirmView
from rest_framework import permissions, routers

from data_ocean.views import RegisterView
from business_register.views.company_views import CompanyView
from business_register.views.kved_views import KvedView
from business_register.views.rfop_views import RfopView, FopView
from business_register.views.ruo_views import RuoView
from location_register.views.ratu_viewsets import RegionView, CityView, StreetView, CityDistrictView, DistrictView
from location_register.views.drv_viewsets import DrvBuildingViewSet
from users.views import CurrentUserProfileView


router = routers.DefaultRouter()

router.register(r'rfop', RfopView, basename='rfop')
router.register(r'rfop/<int:pk>', RfopView, basename='rfop_item')
router.register(r'fop', FopView, basename='fop')
router.register(r'fop/<int:pk>', FopView, basename='fop_item')
router.register(r'ruo', RuoView, basename='ruo')
router.register(r'ruo/<int:pk>', RuoView, basename='ruo_item')
router.register(r'kved', KvedView, basename='kved')
router.register(r'kved/<int:pk>', KvedView, basename='kved_item')
router.register(r'region', RegionView, basename='region')
router.register(r'region/<int:pk>', RegionView, basename='region_item')
router.register(r'city', CityView, basename='city')
router.register(r'city/<int:pk>', CityView, basename='city_item')
router.register(r'street', StreetView, basename='street')
router.register(r'street/<int:pk>', StreetView, basename='street_item')
router.register(r'citydistrict', CityDistrictView, basename='citydistrict')
router.register(r'citydistrict/<int:pk>', CityDistrictView, basename='citydistrict_item')
router.register(r'district', DistrictView, basename='district')
router.register(r'district/<int:pk>', DistrictView, basename='district_item')
router.register(r'drvbuilding', DrvBuildingViewSet, basename='drvbuilding')
router.register(r'drvbuilding/<int:pk>', DrvBuildingViewSet, basename='drvbuilding_item')
router.register(r'company', CompanyView, basename='company')
router.register(r'company/<int:pk>', CompanyView, basename='company_item')
router.register(r'register', RegisterView, basename='register')
router.register(r'register/<int:pk>', RegisterView, basename='registeritem')

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path('admin/', admin.site.urls),

    re_path(r'^api/rest-auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(),
            name='password_reset_confirm'),

    path('', TemplateView.as_view(template_name='users/index.html')),
    path('api/accounts/profile/', TemplateView.as_view(template_name='users/profile.html')),
    path('api/accounts/', include('allauth.urls')),

    path('api/rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/rest-auth/profile/', CurrentUserProfileView.as_view()),
    path('api/rest-auth/', include('rest_auth.urls')),

    path('api/users/', include('users.urls')),

    path('api/', include(router.urls)),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += [
        path('debug-rest-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]
