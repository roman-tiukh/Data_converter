from django.urls import path
from payment_system.views.project_views import ProjectCreateView, ProjectUpdateView

urlpatterns = [
    path('project/create/', ProjectCreateView.as_view()),
    path('project/update/', ProjectUpdateView.as_view()),
]
