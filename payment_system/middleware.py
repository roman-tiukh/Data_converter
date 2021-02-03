from django.http import HttpRequest, HttpResponse
from payment_system.models import Project


class RequestsLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response: HttpResponse = self.get_response(request)
        project: Project = getattr(request, 'project', None)

        if project and isinstance(project, Project) and response.status_code // 100 != 5:
            current_p2s = project.active_p2s
            current_p2s.requests_left -= 1
            current_p2s.requests_used += 1
            current_p2s.save()
        return response
