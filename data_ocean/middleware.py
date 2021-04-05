from payment_system.models import Project
from django.utils import translation


class DataOceanLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # checking if the language was already set from the header
        if request.headers.get('Accept-Language'):
            return self.get_response(request)
        # getting language from user`s project
        project = getattr(request, 'project', None)
        if project and isinstance(project, Project):
            translation.activate(project.owner.language)
            request.LANGUAGE_CODE = translation.get_language()
            return self.get_response(request)
