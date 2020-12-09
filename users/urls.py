from django.urls import path
from users import views
from users.views import QuestionCreateView

urlpatterns = [
    path('', views.UserListView.as_view()),
    path('question/create/', QuestionCreateView.as_view()),
]
