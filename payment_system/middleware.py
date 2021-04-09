from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from payment_system.models import Project


def permission_denied(message: str):
    return JsonResponse({'detail': message}, status=403)


class ProjectAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def authenticate_project(self, request):
        auth_header = request.headers.get('authorization')
        if not auth_header or type(auth_header) != str:
            return None, None
        auth_words = auth_header.split()
        if len(auth_words) != 2:
            return None, None

        keyword = auth_words[0]
        token = auth_words[1]

        if keyword in (settings.PROJECT_PLATFORM_TOKEN_KEYWORD, settings.PROJECT_TOKEN_KEYWORD):
            try:
                project = Project.objects.get(token=token)
                if project.is_disabled:
                    return None, None
                return project, keyword
            except Project.DoesNotExist:
                return None, None
        return None, None

    def set_locale(self, request, project: Project):
        # checking if the language was already set from the header
        if request.headers.get('Accept-Language'):
            return

        translation.activate(project.owner.language)
        request.LANGUAGE_CODE = translation.get_language()

    def __call__(self, request: HttpRequest):
        project, keyword = self.authenticate_project(request)
        is_project_authenticated = bool(project and isinstance(project, Project))
        if is_project_authenticated:
            current_p2s = project.active_p2s

            if keyword == settings.PROJECT_TOKEN_KEYWORD:
                if current_p2s.requests_left <= 0:
                    return permission_denied(_('You have 0 requests left'))
            elif keyword == settings.PROJECT_PLATFORM_TOKEN_KEYWORD:
                if current_p2s.platform_requests_left <= 0:
                    return permission_denied(_('You have 0 views left'))
            else:
                return permission_denied(_('You do not have permission to perform this action.'))

            if current_p2s.expiring_date <= timezone.localdate():
                current_p2s.expire()

            request.project = project
            request.current_p2s = current_p2s
            self.set_locale(request, project)
            response: HttpResponse = self.get_response(request)

            if response.status_code // 100 != 5 and getattr(request, '_decrease_requests_counter', True):
                if keyword == settings.PROJECT_PLATFORM_TOKEN_KEYWORD:
                    current_p2s.platform_requests_left -= 1
                    current_p2s.platform_requests_used += 1
                    current_p2s.save(update_fields=[
                        'platform_requests_left',
                        'platform_requests_used',
                    ])
                else:
                    current_p2s.requests_left -= 1
                    current_p2s.requests_used += 1
                    current_p2s.save(update_fields=[
                        'requests_left',
                        'requests_used',
                    ])
            return response
        return self.get_response(request)
