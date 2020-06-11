from data_ocean.models import Register
from data_ocean.serializers import RegisterSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class Views (GenericAPIView):
    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data # pagination data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
        return Response(data)


class RegisterView(viewsets.ReadOnlyModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer

    def list(self, request):
        queryset = self.get_queryset()
        results = self.paginate_queryset(queryset)
        serializer = RegisterSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        register = get_object_or_404(queryset, pk=pk)
        serializer = RegisterSerializer(register)
        return Response(serializer.data)
