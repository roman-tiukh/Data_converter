from rest_framework import generics, views
from rest_framework.response import Response

from users import models
from users import serializers


class UserListView(generics.ListAPIView):
    queryset = models.DataOceanUser.objects.all()
    serializer_class = serializers.DataOceanUserSerializer


class CurrentUserProfileView(views.APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response(serializers.DataOceanUserSerializer(request.user).data, status=200)
        return Response(status=403)
