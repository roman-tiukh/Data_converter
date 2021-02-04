import time
from datetime import timedelta, datetime

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from business_register.models.company_models import Company, CompanyToKved, CompanyType
from business_register.models.fop_models import Fop
from business_register.models.pep_models import Pep, CompanyLinkWithPep, RelatedPersonsLink
from data_ocean.models import Register
from stats import logic
from stats.serializers import TopKvedSerializer, CompanyTypeCountSerializer
from .models import ApiUsageTracking
from .cache_warming import WarmedCacheGetAPIView
from payment_system.models import UserProject


class StatsTestView(WarmedCacheGetAPIView):
    cache_timeout = 30

    @staticmethod
    def get_data_for_response():
        time.sleep(20)
        return {
            "test_data": 'data_for_test',
            "1": 321,
        }


class ApiUsageMeView(views.APIView):
    def get(self, request):
        date_to = timezone.now()
        date_from = date_to - timedelta(days=30)

        days = logic.get_api_usage_by_day(
            date_from=date_from,
            date_to=date_to,
            user_id=request.user.id
        )

        now = datetime.now()
        current_month = ApiUsageTracking.objects.filter(
            user=request.user,
            timestamp__month=now.month,
            timestamp__year=now.year,
        ).count()

        prev_month = ApiUsageTracking.objects.filter(
            user=request.user,
            timestamp__month=12 if now.month == 1 else now.month - 1,
            timestamp__year=now.year - 1 if now.month == 1 else now.year,
        ).count()

        return Response({
            'days': days,
            'current_month': current_month,
            'prev_month': prev_month,
        }, status=200)


class ProfileStatsView(views.APIView):
    def get(self, request):
        api_requests = ApiUsageTracking.objects.filter(
            user_id=request.user.id
        ).count()
        endpoints = Register.objects.count()
        return Response({
            "api_requests": api_requests,
            "endpoints": endpoints,
        }, status=200)


class TopKvedsView(WarmedCacheGetAPIView):
    @staticmethod
    def get_data_for_response():
        qs = CompanyToKved.objects.select_related(
            'kved', 'kved__group', 'kved__section', 'kved__division',
        ).exclude(
            kved__code='not_valid'
        ).values(
            'kved'
        ).annotate(
            count_companies_with_kved=Count('kved')
        ).order_by('-count_companies_with_kved')[:10]
        return TopKvedSerializer(qs, many=True).data


class CompanyTypeCountView(WarmedCacheGetAPIView):
    @staticmethod
    def get_data_for_response():
        qs = CompanyType.objects.annotate(
            count_companies=Count('company')
        ).order_by('-count_companies').all()
        return CompanyTypeCountSerializer(qs, many=True).data


class RegisteredCompaniesCountView(WarmedCacheGetAPIView):
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RegisteredCompaniesCountFilterSet

    @staticmethod
    def get_data_for_response():
        return {
            'company_count': Company.objects.count()
        }


class RegisteredFopsCountView(WarmedCacheGetAPIView):
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RegisteredFopsCountFilterSet

    @staticmethod
    def get_data_for_response():
        return {
            'company_count': Fop.objects.count()
        }


class UsersInProjectsView(views.APIView):
    def get(self, request):
        user = request.user
        user_projects = UserProject.objects.filter(user=user).values_list('project', flat=True)
        users_count = UserProject.objects.filter(project__in=list(user_projects)).order_by(
            'user'
        ).distinct('user').count()
        return Response({
            'users_count': users_count
        }, status=200)


class PepsCountView(WarmedCacheGetAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_data_for_response():
        return {
            'peps_count': Pep.objects.filter(is_pep=True).count()
        }


class PepRelatedPersonsCountView(WarmedCacheGetAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_data_for_response():
        return {
            'pep_related_persons_count': Pep.objects.filter(is_pep=False).count()
        }


class PepLinkedCompaniesCountView(WarmedCacheGetAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_data_for_response():
        return CompanyLinkWithPep.objects.aggregate(
            pep_related_companies_count=Count('company', distinct=True)
        )


class PepRelationCategoriesCountView(WarmedCacheGetAPIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get_data_for_response():
        return {
            'business_pep_relations_count':
                RelatedPersonsLink.objects.filter(category=RelatedPersonsLink.BUSINESS).count(),
            'personal_pep_relations_count':
                RelatedPersonsLink.objects.filter(category=RelatedPersonsLink.PERSONAL).count(),
            'family_pep_relations_count':
                RelatedPersonsLink.objects.filter(category=RelatedPersonsLink.FAMILY).count(),
        }
