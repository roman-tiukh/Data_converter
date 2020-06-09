from rest_framework import generics

from users import models
from users import serializers


class UserListView(generics.ListAPIView):
    queryset = models.DataOceanUser.objects.all()
    serializer_class = serializers.DataOceanUserSerializer
