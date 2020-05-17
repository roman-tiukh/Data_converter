from data_ocean.models.common_models import Authority, Status, TaxpayerType
from data_ocean.models.company_models import Bylaw, CompanyType, Company, Assignee, BancruptcyReadjustment, CompanyDetail, CompanyToKved, ExchangeDataCompany, FounderFull, Predecessor, CompanyToPredecessor, Signer, TerminationStarted
from data_ocean.models.kved_models import Kved
from data_ocean.models.main import DataOceanModel
from data_ocean.models.ruo_models import State
from data_ocean.serializers.company_serializers import BylawSerializer, CompanyTypeSerializer, CompanySerializer, AssigneeSerializer, BancruptcyReadjustmentSerializer, CompanyDetailSerializer, CompanyToKvedSerializer, ExchangeDataCompanySerializer, FounderFullSerializer, PredecessorSerializer, CompanyToPredecessorSerializer, SignerSerializer, TerminationStartedSerializer

from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class BylawView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Bylaw.objects.all()
    serializer_class = BylawSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = BylawSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        bylaw = get_object_or_404(queryset, pk=pk)
        serializer = BylawSerializer(bylaw)
        return Response(serializer.data)

class CompanyTypeView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = CompanyType.objects.all()
    serializer_class = CompanyTypeSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanyTypeSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company_type = get_object_or_404(queryset, pk=pk)
        serializer = CompanyTypeSerializer(company_type)
        return Response(serializer.data)

class CompanyView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanySerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company = get_object_or_404(queryset, pk=pk)
        serializer = CompanySerializer(company)
        return Response(serializer.data)        

class AssigneeView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Assignee.objects.all()
    serializer_class = AssigneeSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = AssigneeSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        assignee = get_object_or_404(queryset, pk=pk)
        serializer = AssigneeSerializer(assignee)
        return Response(serializer.data)

class BancruptcyReadjustmentView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = BancruptcyReadjustment.objects.all()
    serializer_class = BancruptcyReadjustmentSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = BancruptcyReadjustmentSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        bancruptcy_readjustment = get_object_or_404(queryset, pk=pk)
        serializer = BancruptcyReadjustmentSerializer(bancruptcy_readjustment)
        return Response(serializer.data)

class CompanyDetailView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = CompanyDetail.objects.all()
    serializer_class = CompanyDetailSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanyDetailSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company_detail = get_object_or_404(queryset, pk=pk)
        serializer = CompanyDetailSerializer(company_detail)
        return Response(serializer.data)

class CompanyToKvedView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = CompanyToKved.objects.all()
    serializer_class = CompanyToKvedSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanyToKvedSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company_to_kved = get_object_or_404(queryset, pk=pk)
        serializer = CompanyToKvedSerializer(company_to_kved)
        return Response(serializer.data)

class ExchangeDataCompanyView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = ExchangeDataCompany.objects.all()
    serializer_class = ExchangeDataCompanySerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = ExchangeDataCompanySerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        exchange_data_company = get_object_or_404(queryset, pk=pk)
        serializer = ExchangeDataCompanySerializer(exchange_data_company)
        return Response(serializer.data)

class FounderFullView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = FounderFull.objects.all()
    serializer_class = FounderFullSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = FounderFullSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        founder_full = get_object_or_404(queryset, pk=pk)
        serializer = FounderFullSerializer(founder_full)
        return Response(serializer.data)

class PredecessorView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Predecessor.objects.all()
    serializer_class = PredecessorSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = PredecessorSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        predecessor = get_object_or_404(queryset, pk=pk)
        serializer = PredecessorSerializer(predecessor)
        return Response(serializer.data)

class CompanyToPredecessorView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = CompanyToPredecessor.objects.all()
    serializer_class = CompanyToPredecessorSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = CompanyToPredecessorSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        company_to_predecessor = get_object_or_404(queryset, pk=pk)
        serializer = CompanyToPredecessorSerializer(company_to_predecessor)
        return Response(serializer.data)

class SignerView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = Signer.objects.all()
    serializer_class = SignerSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = SignerSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        signer = get_object_or_404(queryset, pk=pk)
        serializer = SignerSerializer(signer)
        return Response(serializer.data)

class TerminationStartedView(viewsets.ReadOnlyModelViewSet, PageNumberPagination):
    queryset = TerminationStarted.objects.all()
    serializer_class = TerminationStartedSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = TerminationStartedSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        termination_started = get_object_or_404(queryset, pk=pk)
        serializer = TerminationStartedSerializer(termination_started)
        return Response(serializer.data)