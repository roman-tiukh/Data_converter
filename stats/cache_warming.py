from abc import abstractmethod, ABC

from django.core.cache import cache
from rest_framework import views
from rest_framework.response import Response


class WarmedCacheGetAPIView(views.APIView, ABC):
    cache_timeout = 60 * 60 * 24  # seconds

    @classmethod
    def get_cache_key(cls):
        return f'{cls.__module__}.{cls.__name__}'

    @classmethod
    def warm_up_cache(cls):
        cls.set_cache_data(cls.get_data_for_response())

    @classmethod
    def set_cache_data(cls, data):
        cache.set(cls.get_cache_key(), data, cls.cache_timeout)

    @staticmethod
    @abstractmethod
    def get_data_for_response():
        """
        Must return data for response,
        data will be cached with warming support
        """

    def get(self, request):
        data = cache.get(self.get_cache_key())
        if data is None:
            data = self.get_data_for_response()
            self.set_cache_data(data)
        return Response(data, status=200)

