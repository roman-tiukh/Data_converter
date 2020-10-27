from django.urls import path
from payment_system.views.project_views import ProjectCreateView

urlpatterns = [
    path('project/create/', ProjectCreateView.as_view()),
]
