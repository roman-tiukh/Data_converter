from django.urls import path
from users import views

urlpatterns = [
    path('', views.UserListView.as_view()),
]
